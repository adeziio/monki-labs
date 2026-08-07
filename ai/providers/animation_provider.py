from pathlib import Path

import torch

from PIL import Image

from moviepy import ImageClip

from diffusers import WanImageToVideoPipeline
from diffusers.utils import export_to_video


class AnimationProvider:


    def __init__(
        self,
        config,
        device="cpu"
    ):


        self.device = device


        animation_config = (
            config["ai_models"]
            ["models"]
            ["animation_model"]
        )


        self.enabled = (
            animation_config.get(
                "enabled",
                True
            )
        )


        self.model_name = (
            animation_config.get(
                "model",
                "Wan-AI/Wan2.1-I2V-14B-Diffusers"
            )
        )


        self.frames = (
            animation_config.get(
                "frames",
                17
            )
        )


        self.fps = (
            animation_config.get(
                "fps",
                8
            )
        )


        self.pipeline = None


        # Only use Wan when a CUDA GPU is available.
        if (
            self.enabled
            and
            self.device == "cuda"
        ):

            self.log(
                f"Loading animation model: {self.model_name}"
            )


            self.pipeline = (
                WanImageToVideoPipeline
                .from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16
                )
            )


            self.pipeline.to(
                self.device
            )


            self.pipeline.enable_vae_slicing()

            self.pipeline.enable_vae_tiling()


        else:

            self.log(
                "CUDA not available. Using MoviePy animation fallback."
            )



    def log(
        self,
        message
    ):

        print(
            f"[Animation Provider] {message}"
        )



    def generate(
        self,
        image_path,
        output_path
    ):


        # --------------------------------------------------
        # GPU Path (Wan Image-to-Video)
        # --------------------------------------------------

        if self.pipeline is not None:


            image = (
                Image.open(
                    image_path
                )
                .convert(
                    "RGB"
                )
            )


            self.log(
                f"Animating {image_path}"
            )


            result = (
                self.pipeline(
                    prompt=(
                        "Animate this image with smooth cartoon motion. "
                        "Keep the character consistent. "
                        "Add natural movement and cinematic animation."
                    ),
                    image=image,
                    num_frames=self.frames
                )
            )


            frames = (
                result.frames[0]
            )


            output_path = Path(
                output_path
            )


            output_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )


            export_to_video(
                frames,
                str(output_path),
                fps=self.fps
            )


            return str(
                output_path
            )


        # --------------------------------------------------
        # CPU Fallback
        # --------------------------------------------------

        self.log(
            f"Creating fallback animation for {image_path}"
        )


        output_path = Path(
            output_path
        )


        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        clip = (
            ImageClip(
                str(image_path)
            )
            .with_duration(
                3
            )
        )


        clip.write_videofile(
            str(output_path),
            fps=24,
            codec="libx264",
            audio=False
        )


        return str(
            output_path
        )
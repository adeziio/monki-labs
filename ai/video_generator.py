from pathlib import Path
import re

import torch

from moviepy import (
    VideoFileClip,
    concatenate_videoclips
)

from diffusers import LTX2Pipeline

from diffusers.pipelines.ltx2.export_utils import (
    encode_video
)

from diffusers.pipelines.ltx2.utils import (
    DEFAULT_NEGATIVE_PROMPT
)

from ai.base_ai_service import BaseAIService
from ai.prompt_generator import PromptGenerator


class VideoGenerator(
    BaseAIService
):

    def __init__(
        self,
        config
    ):

        super().__init__(
            config
        )

        self.config = config

        self.hardware = (
            config.get(
                "hardware",
                {}
            )
        )

        self.video_config = (
            config["ai_models"]
            ["models"]
            ["video_model"]
        )

        content_config = (
            config["content"]
        )

        self.active_category = (
            content_config[
                "active_category"
            ]
        )

        self.category_config = (
            content_config[
                "categories"
            ][
                self.active_category
            ]
        )

        self.video_output_config = (
            self.category_config[
                "video"
            ]
        )

        self.generation_config = (
            self.category_config[
                "generation"
            ]
        )

        self.prompt_generator = (
            PromptGenerator(
                config
            )
        )

        self.pipeline = None

        self.output_root = Path(
            "media/output"
        )

        self.category_output_directory = (
            self.output_root
            /
            self.get_category_directory_name()
        )

        self.run_directory = (
            self.create_run_directory()
        )

        self.clip_output_directory = (
            self.run_directory
        )

    def get_category_directory_name(
        self
    ):

        category_name = (
            self.category_config
            .get(
                "name",
                self.active_category
            )
        )

        category_name = str(
            category_name
        ).strip()

        if not category_name:

            category_name = (
                self.active_category
            )

        category_name = re.sub(
            r'[<>:"/\\|?*]',
            "_",
            category_name
        )

        category_name = re.sub(
            r"\s+",
            " ",
            category_name
        )

        return category_name

    def create_run_directory(
        self
    ):

        self.category_output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        existing_numbers = []

        for path in (
            self.category_output_directory.iterdir()
        ):

            if not path.is_dir():

                continue

            if not path.name.isdigit():

                continue

            existing_numbers.append(
                int(
                    path.name
                )
            )

        if existing_numbers:

            next_number = (
                max(
                    existing_numbers
                )
                +
                1
            )

        else:

            next_number = 1

        run_directory = (
            self.category_output_directory
            /
            f"{next_number:03}"
        )

        run_directory.mkdir(
            parents=True,
            exist_ok=False
        )

        self.log(
            f"Output run directory: "
            f"{run_directory}"
        )

        return run_directory

    def get_device(
        self
    ):

        device = (
            self.hardware[
                "device"
            ]
        )

        if device == "auto":

            if torch.cuda.is_available():

                return "cuda"

            return "cpu"

        if device not in (
            "cpu",
            "cuda",
            "mps"
        ):

            raise ValueError(
                "Unsupported execution device: "
                f"{device}"
            )

        if (
            device == "cuda"
            and
            not torch.cuda.is_available()
        ):

            fallback = (
                self.hardware.get(
                    "fallback"
                )
            )

            if fallback:

                self.log(
                    "CUDA requested but unavailable. "
                    f"Using configured fallback: {fallback}"
                )

                return fallback

            raise RuntimeError(
                "CUDA requested but unavailable "
                "and no fallback device is configured."
            )

        return device

    def get_dtype(
        self,
        device
    ):

        dtype_name = (
            self.hardware[
                "torch_dtype"
            ]
        )

        dtype_map = {

            "float32":
            torch.float32,

            "float16":
            torch.float16,

            "bfloat16":
            torch.bfloat16

        }

        if dtype_name not in dtype_map:

            raise ValueError(
                "Unsupported torch dtype: "
                f"{dtype_name}"
            )

        if device == "cpu":

            return torch.float32

        return dtype_map[
            dtype_name
        ]

    def get_generation_resolution(
        self
    ):

        resolution = (
            self.video_config[
                "generation_resolution"
            ]
        )

        width = int(
            resolution[
                "width"
            ]
        )

        height = int(
            resolution[
                "height"
            ]
        )

        if width <= 0 or height <= 0:

            raise ValueError(
                "LTX generation resolution "
                "must contain positive values."
            )

        if width % 32 != 0:

            raise ValueError(
                "LTX generation width must "
                "be divisible by 32."
            )

        if height % 32 != 0:

            raise ValueError(
                "LTX generation height must "
                "be divisible by 32."
            )

        return (
            width,
            height
        )

    def get_generation_fps(
        self
    ):

        fps = float(
            self.video_config[
                "generation_fps"
            ]
        )

        if fps <= 0:

            raise ValueError(
                "LTX generation FPS must "
                "be greater than zero."
            )

        return fps

    def get_output_resolution(
        self
    ):

        resolution = (
            self.video_output_config[
                "resolution"
            ]
        )

        width = int(
            resolution[
                "width"
            ]
        )

        height = int(
            resolution[
                "height"
            ]
        )

        if width <= 0 or height <= 0:

            raise ValueError(
                "Final video resolution must "
                "contain positive values."
            )

        return (
            width,
            height
        )

    def get_output_aspect_ratio(
        self
    ):

        return (
            self.video_output_config[
                "aspect_ratio"
            ]
        )

    def get_output_format(
        self
    ):

        return (
            self.video_output_config[
                "format"
            ]
        )

    def get_clip_duration(
        self
    ):

        duration = float(
            self.video_output_config[
                "duration_seconds"
            ]
        )

        if duration <= 0:

            raise ValueError(
                "Video duration must "
                "be greater than zero."
            )

        return duration

    def get_output_fps(
        self
    ):

        fps = float(
            self.video_output_config[
                "fps"
            ]
        )

        if fps <= 0:

            raise ValueError(
                "Output FPS must "
                "be greater than zero."
            )

        return fps

    def get_frame_count(
        self,
        duration
    ):

        model_fps = (
            self.get_generation_fps()
        )

        raw_frame_count = (
            duration
            *
            model_fps
        )

        frame_count = (
            round(
                (
                    raw_frame_count
                    -
                    1
                )
                /
                8
            )
            *
            8
            +
            1
        )

        return frame_count

    def get_inference_steps(
        self,
        device
    ):

        steps_config = (
            self.video_config[
                "steps"
            ]
        )

        if device not in steps_config:

            raise ValueError(
                "No LTX inference steps "
                f"configured for device: {device}"
            )

        steps = int(
            steps_config[
                device
            ]
        )

        if steps <= 0:

            raise ValueError(
                "LTX inference steps "
                "must be greater than zero."
            )

        return steps

    def load_pipeline(
        self
    ):

        if self.pipeline is not None:

            return

        device = (
            self.get_device()
        )

        dtype = (
            self.get_dtype(
                device
            )
        )

        model_name = (
            self.video_config[
                "model"
            ]
        )

        provider = (
            self.video_config[
                "provider"
            ]
        )

        if provider.lower() != "ltx":

            raise RuntimeError(
                "Unsupported video provider: "
                f"{provider}"
            )

        self.log(
            f"Loading video model: "
            f"{model_name}"
        )

        self.log(
            f"Execution device: "
            f"{device}"
        )

        self.log(
            f"Model dtype: "
            f"{dtype}"
        )

        self.pipeline = (
            LTX2Pipeline.from_pretrained(
                model_name,
                torch_dtype=dtype
            )
        )

        if device == "cuda":

            self.log(
                "Benchmark mode: "
                "loading entire pipeline directly onto CUDA."
            )

            self.pipeline.to(
                "cuda"
            )

        elif device == "mps":

            self.pipeline.to(
                device
            )

        else:

            self.pipeline.enable_sequential_cpu_offload()

    def generate_clip(
        self,
        prompt,
        output_path
    ):

        self.log(
            f"Generating audio-video clip: "
            f"{prompt}"
        )

        device = (
            self.get_device()
        )

        model_width, model_height = (
            self.get_generation_resolution()
        )

        model_fps = (
            self.get_generation_fps()
        )

        steps = (
            self.get_inference_steps(
                device
            )
        )

        duration = (
            self.get_clip_duration()
        )

        frames = (
            self.get_frame_count(
                duration
            )
        )

        guidance_scale = float(
            self.video_config[
                "guidance_scale"
            ]
        )

        audio_guidance_scale = float(
            self.video_config[
                "audio_guidance_scale"
            ]
        )

        # STG is intentionally disabled.
        #
        # LTX-2.3 requires explicit STG block indices
        # whenever STG is enabled. Keeping this at zero
        # avoids that requirement and reduces memory usage.
        audio_stg_scale = 0.0

        audio_modality_scale = float(
            self.video_config[
                "audio_modality_scale"
            ]
        )

        negative_prompt = (
            self.video_config.get(
                "negative_prompt",
                DEFAULT_NEGATIVE_PROMPT
            )
        )

        output_width, output_height = (
            self.get_output_resolution()
        )

        output_fps = (
            self.get_output_fps()
        )

        actual_duration = (
            frames
            /
            model_fps
        )

        self.log(
            f"Final content resolution: "
            f"{output_width}x{output_height}"
        )

        self.log(
            f"Final aspect ratio: "
            f"{self.get_output_aspect_ratio()}"
        )

        self.log(
            f"Model generation resolution: "
            f"{model_width}x{model_height}"
        )

        self.log(
            f"Target clip duration: "
            f"{duration:.1f} seconds"
        )

        self.log(
            f"Model generation FPS: "
            f"{model_fps:g}"
        )

        self.log(
            f"Final output FPS: "
            f"{output_fps:g}"
        )

        self.log(
            f"Generating {frames} frames"
        )

        self.log(
            f"Model clip duration: "
            f"{actual_duration:.3f} seconds"
        )

        self.log(
            f"Inference steps: "
            f"{steps}"
        )

        self.log(
            "Spatio-Temporal Guidance: disabled"
        )

        video, audio = (
            self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=model_width,
                height=model_height,
                num_frames=frames,
                frame_rate=model_fps,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                audio_guidance_scale=audio_guidance_scale,
                audio_stg_scale=audio_stg_scale,
                audio_modality_scale=audio_modality_scale,
                output_type="np",
                return_dict=False
            )
        )

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        encode_video(
            video[0],
            fps=model_fps,
            audio=audio[0]
            .float()
            .cpu(),
            audio_sample_rate=(
                self.pipeline
                .vocoder
                .config
                .output_sampling_rate
            ),
            output_path=str(
                output_path
            )
        )

        return str(
            output_path
        )

    def combine_clips(
        self,
        clip_paths
    ):

        self.log(
            "Combining generated audio-video clips"
        )

        clips = []

        for clip_path in clip_paths:

            clips.append(
                VideoFileClip(
                    clip_path
                )
            )

        if not clips:

            raise RuntimeError(
                "No video clips were generated."
            )

        final_video = (
            concatenate_videoclips(
                clips,
                method="compose"
            )
        )

        return (
            final_video,
            clips
        )

    def generate(
        self
    ):

        self.log(
            "Starting short-form "
            "audio-video generation"
        )

        clip_count = int(
            self.generation_config[
                "clip_count"
            ]
        )

        if clip_count <= 0:

            raise ValueError(
                "Generation clip count "
                "must be greater than zero."
            )

        prompts = (
            self.prompt_generator
            .generate(
                clip_count
            )
        )

        if not prompts:

            raise RuntimeError(
                "No video prompts "
                "were generated."
            )

        self.load_pipeline()

        clip_paths = []

        for index, prompt in enumerate(
            prompts,
            start=1
        ):

            output_path = (
                self.clip_output_directory
                /
                f"clip_{index:03}.mp4"
            )

            clip_path = (
                self.generate_clip(
                    prompt,
                    output_path
                )
            )

            clip_paths.append(
                clip_path
            )

        final_video, clips = (
            self.combine_clips(
                clip_paths
            )
        )

        output_format = (
            self.get_output_format()
        )

        if output_format.lower() != "mp4":

            raise ValueError(
                "The current LTX video "
                "export pipeline requires "
                "MP4 output."
            )

        output_path = (
            self.run_directory
            /
            f"episode.{output_format}"
        )

        output_fps = (
            self.get_output_fps()
        )

        final_video.write_videofile(
            str(output_path),
            fps=output_fps,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=(
                str(
                    self.run_directory
                    /
                    "temp_audio.m4a"
                )
            ),
            remove_temp=True
        )

        for clip in clips:

            clip.close()

        final_video.close()

        self.log(
            f"Final audio-video created: "
            f"{output_path}"
        )

        return {
            "output": str(
                output_path
            ),
            "clips": clip_paths,
            "prompts": prompts
        }
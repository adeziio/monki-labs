from pathlib import Path

import torch

from diffusers import StableDiffusionPipeline



class StableDiffusionProvider:


    def __init__(self, config, device="cpu"):


        self.device = device


        image_config = (
            config["ai_models"]
            ["models"]
            ["image_model"]
        )


        self.output_directory = Path(
            image_config.get(
                "output_directory",
                "media/scenes"
            )
        )


        self.output_directory.mkdir(
            parents=True,
            exist_ok=True
        )


        model_name = (
            image_config.get(
                "model",
                "runwayml/stable-diffusion-v1-5"
            )
        )


        self.pipeline = (
            StableDiffusionPipeline
            .from_pretrained(
                model_name,
                torch_dtype=
                torch.float16
                if device == "cuda"
                else torch.float32
            )
        )


        self.pipeline.to(
            device
        )



    def generate(
        self,
        prompt,
        filename,
        output_directory
    ):


        image = (
            self.pipeline(
                prompt
            )
            .images[0]
        )


        output_directory.mkdir(
            parents=True,
            exist_ok=True
        )


        output = (
            output_directory
            /
            filename
        )


        image.save(
            output
        )


        return str(output)
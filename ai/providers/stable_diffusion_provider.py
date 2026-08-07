from pathlib import Path

import torch

from diffusers import StableDiffusionPipeline


class StableDiffusionProvider:


    def __init__(
        self,
        config
    ):


        hardware = (
            config["hardware"]
        )


        self.device = (
            hardware["device"]
        )


        torch_dtype = (

            torch.float16

            if

            hardware["torch_dtype"]
            == "float16"

            else

            torch.float32

        )


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
                torch_dtype=torch_dtype
            )
        )


        self.pipeline.to(
            self.device
        )


    def trim_prompt(
        self,
        prompt,
        max_tokens=70
    ):

        tokenizer = (
            self.pipeline.tokenizer
        )


        encoded = tokenizer(
            prompt,
            truncation=True,
            max_length=max_tokens,
            return_tensors="pt"
        )


        trimmed_prompt = (
            tokenizer.decode(
                encoded.input_ids[0],
                skip_special_tokens=True
            )
        )


        if trimmed_prompt != prompt:

            print(
                "[Stable Diffusion] Prompt trimmed"
            )

            print(
                f"Original length: {len(prompt)} characters"
            )

            print(
                f"Final length: {len(trimmed_prompt)} characters"
            )


        return trimmed_prompt



    def generate(
        self,
        prompt,
        negative_prompt,
        filename,
        output_directory
    ):


        prompt = self.trim_prompt(
            prompt
        )


        negative_prompt = self.trim_prompt(
            negative_prompt
        )


        image = (
            self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt
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
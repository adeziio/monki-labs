from pathlib import Path

import torch

from PIL import Image

from diffusers import StableDiffusionImg2ImgPipeline


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


        model_name = (
            image_config.get(
                "model",
                "runwayml/stable-diffusion-v1-5"
            )
        )


        self.pipeline = (

            StableDiffusionImg2ImgPipeline
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


        return trimmed_prompt



    def generate(
        self,
        prompt,
        negative_prompt,
        filename,
        output_directory,
        reference_image
    ):


        prompt = self.trim_prompt(
            prompt
        )


        negative_prompt = self.trim_prompt(
            negative_prompt
        )


        image = Image.open(
            reference_image
        ).convert(
            "RGB"
        )


        image = image.resize(
            (512, 512)
        )


        print(
            "[Stable Diffusion] Using reference:"
        )

        print(
            reference_image
        )


        result = (

            self.pipeline(

                prompt=prompt,

                image=image,

                negative_prompt=negative_prompt,

                strength=0.55,

                guidance_scale=7.5

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


        result.save(
            output
        )


        return str(output)
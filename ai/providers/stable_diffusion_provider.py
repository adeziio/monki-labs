from pathlib import Path

import torch

from PIL import Image, ImageOps

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

            if hardware["torch_dtype"] == "float16"

            else torch.float32

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


        return tokenizer.decode(
            encoded.input_ids[0],
            skip_special_tokens=True
        )



    def create_reference_sheet(
        self,
        reference_images
    ):

        images = []


        for path in reference_images:

            image = Image.open(
                path
            ).convert(
                "RGB"
            )


            image.thumbnail(
                (256,256)
            )


            canvas = Image.new(
                "RGB",
                (256,256),
                "white"
            )


            canvas.paste(
                image,
                (
                    (256-image.width)//2,
                    (256-image.height)//2
                )
            )


            images.append(
                canvas
            )


        sheet = Image.new(
            "RGB",
            (
                256 * len(images),
                256
            )
        )


        for index, image in enumerate(images):

            sheet.paste(
                image,
                (
                    index * 256,
                    0
                )
            )


        return sheet.resize(
            (512,512)
        )



    def generate(
        self,
        prompt,
        negative_prompt,
        filename,
        output_directory,
        reference_images
    ):


        prompt = self.trim_prompt(
            prompt
        )


        negative_prompt = self.trim_prompt(
            negative_prompt
        )


        reference = (
            self.create_reference_sheet(
                reference_images
            )
        )


        print(
            "[Stable Diffusion] Using references:"
        )


        for image in reference_images:

            print(
                image
            )


        result = (
            self.pipeline(
                prompt=prompt,
                image=reference,
                negative_prompt=negative_prompt,
                strength=0.65,
                guidance_scale=8.0
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
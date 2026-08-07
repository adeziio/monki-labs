from pathlib import Path

import torch

from diffusers import FluxPipeline


class FluxProvider:


    def __init__(
        self,
        config,
        lora_path=None
    ):

        hardware = (
            config["hardware"]
        )


        self.device = (
            hardware["device"]
        )


        torch_dtype = (

            torch.bfloat16
            if self.device == "cuda"
            else torch.float32

        )


        image_config = (
            config["ai_models"]
            ["models"]
            ["image_model"]
        )


        self.model_name = (
            image_config.get(
                "model",
                "black-forest-labs/FLUX.1-schnell"
            )
        )


        if lora_path:

            self.lora_path = Path(
                lora_path
            )

        else:

            self.lora_path = Path(
                image_config["lora_path"]
            )


        print(
            "[FLUX] Loading model..."
        )


        self.pipeline = FluxPipeline.from_pretrained(

            self.model_name,

            torch_dtype=torch_dtype

        )


        print(
            f"[FLUX] Loading LoRA: {self.lora_path}"
        )


        self.pipeline.load_lora_weights(

            str(self.lora_path)

        )


        self.pipeline.to(
            self.device
        )


        print(
            "[FLUX] Ready"
        )



    def generate(
        self,
        prompt,
        filename,
        output_directory
    ):


        print(
            "[FLUX] Generating:"
        )


        print(
            prompt
        )


        result = self.pipeline(

            prompt=prompt,

            height=1024,

            width=1024,

            num_inference_steps=4,

            guidance_scale=1.0

        ).images[0]


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
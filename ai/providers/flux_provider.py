from pathlib import Path

import torch

from diffusers import FluxPipeline


class FluxProvider:

    def __init__(
        self,
        config,
        lora_paths=None
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


        print(
            "[FLUX] Loading model..."
        )


        self.pipeline = FluxPipeline.from_pretrained(

            self.model_name,

            torch_dtype=torch_dtype

        )


        self.loaded_adapters = []


        if lora_paths:

            self.load_loras(
                lora_paths
            )


        self.pipeline.to(
            self.device
        )


        print(
            "[FLUX] Ready"
        )


    def load_loras(
        self,
        lora_paths
    ):

        if isinstance(
            lora_paths,
            (str, Path)
        ):

            lora_paths = [
                lora_paths
            ]


        for index, lora_path in enumerate(
            lora_paths
        ):

            lora_path = Path(
                lora_path
            )


            if not lora_path.exists():

                raise FileNotFoundError(
                    f"LoRA file not found: "
                    f"{lora_path}"
                )


            adapter_name = (
                f"character_{index}"
            )


            print(
                f"[FLUX] Loading LoRA: "
                f"{lora_path}"
            )


            self.pipeline.load_lora_weights(

                str(lora_path),

                adapter_name=adapter_name

            )


            self.loaded_adapters.append(
                adapter_name
            )


    def set_character_loras(
        self,
        lora_paths
    ):

        self.loaded_adapters = []


        self.load_loras(
            lora_paths
        )


        if self.loaded_adapters:

            self.pipeline.set_adapters(
                self.loaded_adapters
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
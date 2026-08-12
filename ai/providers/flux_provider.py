from pathlib import Path
import warnings

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

        self.image_config = (
            image_config
        )

        self.model_name = (
            image_config.get(
                "model",
                "black-forest-labs/FLUX.1-schnell"
            )
        )

        self.height = int(
            image_config.get(
                "height",
                1024
            )
        )

        self.width = int(
            image_config.get(
                "width",
                1024
            )
        )

        self.num_inference_steps = int(
            image_config.get(
                "num_inference_steps",
                4
            )
        )

        self.guidance_scale = float(
            image_config.get(
                "guidance_scale",
                1.0
            )
        )

        print(
            "[FLUX] Loading model..."
        )

        self.pipeline = FluxPipeline.from_pretrained(
            self.model_name,
            torch_dtype=torch_dtype
        )

        self.loaded_adapters = {}

        self.character_adapters = {}

        self.character_strengths = {}

        self.active_character_ids = []

        self.pipeline.to(
            self.device
        )

        print(
            "[FLUX] Ready"
        )

        if lora_paths:

            self.load_loras(
                lora_paths
            )


    def _load_lora_weights(
        self,
        lora_path,
        adapter_name
    ):

        warning_messages = [
            (
                "No LoRA keys associated to "
                "CLIPTextModel found with the prefix="
            ),
            (
                "Already found a `peft_config` "
                "attribute in the model. This will lead "
                "to having multiple adapters in the model."
            )
        ]

        with warnings.catch_warnings():

            for warning_message in warning_messages:

                warnings.filterwarnings(
                    "ignore",
                    message=warning_message,
                    category=UserWarning
                )

            self.pipeline.load_lora_weights(
                str(lora_path),
                adapter_name=adapter_name
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

            if adapter_name in (
                self.loaded_adapters
            ):

                continue

            print(
                f"[FLUX] Loading LoRA: "
                f"{lora_path}"
            )

            self._load_lora_weights(
                lora_path,
                adapter_name
            )

            self.loaded_adapters[
                adapter_name
            ] = lora_path

        if self.loaded_adapters:

            self.pipeline.set_adapters(
                list(
                    self.loaded_adapters.keys()
                )
            )


    def load_character_loras(
        self,
        character_ids,
        lora_paths,
        strengths=None
    ):

        if len(character_ids) != len(
            lora_paths
        ):

            raise ValueError(
                "Character IDs and LoRA paths "
                "must have the same length."
            )

        if strengths is None:

            strengths = [
                1.0
                for _ in character_ids
            ]

        if len(character_ids) != len(
            strengths
        ):

            raise ValueError(
                "Character IDs and LoRA strengths "
                "must have the same length."
            )

        for (
            character_id,
            lora_path,
            strength
        ) in zip(
            character_ids,
            lora_paths,
            strengths
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
                f"character_{character_id}"
            )

            self.character_adapters[
                character_id
            ] = adapter_name

            self.character_strengths[
                character_id
            ] = float(
                strength
            )

            if adapter_name in (
                self.loaded_adapters
            ):

                continue

            print(
                f"[FLUX] Loading LoRA: "
                f"{lora_path}"
            )

            self._load_lora_weights(
                lora_path,
                adapter_name
            )

            self.loaded_adapters[
                adapter_name
            ] = lora_path

        if self.loaded_adapters:

            self.pipeline.set_adapters(
                list(
                    self.loaded_adapters.keys()
                )
            )

        print(
            "[FLUX] Character LoRAs loaded: "
            +
            ", ".join(
                character_ids
            )
        )


    def set_character_loras(
        self,
        character_ids
    ):

        if not character_ids:

            self.pipeline.set_adapters(
                []
            )

            self.active_character_ids = []

            print(
                "[FLUX] No character LoRAs active"
            )

            return

        adapter_names = []

        adapter_weights = []

        for character_id in character_ids:

            if character_id not in (
                self.character_adapters
            ):

                raise ValueError(
                    f"LoRA adapter not loaded "
                    f"for character: "
                    f"{character_id}"
                )

            adapter_name = (
                self.character_adapters[
                    character_id
                ]
            )

            strength = (
                self.character_strengths.get(
                    character_id,
                    1.0
                )
            )

            adapter_names.append(
                adapter_name
            )

            adapter_weights.append(
                strength
            )

        self.pipeline.set_adapters(
            adapter_names,
            adapter_weights=adapter_weights
        )

        self.active_character_ids = list(
            character_ids
        )

        active_display = []

        for character_id, strength in zip(
            character_ids,
            adapter_weights
        ):

            active_display.append(
                f"{character_id}={strength}"
            )

        print(
            "[FLUX] Active character LoRAs: "
            +
            ", ".join(
                active_display
            )
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
            height=self.height,
            width=self.width,
            num_inference_steps=(
                self.num_inference_steps
            ),
            guidance_scale=(
                self.guidance_scale
            )
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
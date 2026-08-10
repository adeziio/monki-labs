from pathlib import Path
import json

import torch

from diffusers import FluxPipeline


PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent


CHARACTERS_CONFIG = (
    PROJECT_ROOT
    / "config"
    / "characters.json"
)


OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "media"
    / "adhoc"
)


MODEL_NAME = (
    "black-forest-labs/FLUX.1-schnell"
)


def load_characters():

    if not CHARACTERS_CONFIG.exists():

        raise FileNotFoundError(
            f"Characters config not found: "
            f"{CHARACTERS_CONFIG}"
        )


    with open(
        CHARACTERS_CONFIG,
        "r",
        encoding="utf-8"
    ) as file:

        config = json.load(file)


    characters = (
        config.get(
            "characters",
            {}
        )
    )


    if not characters:

        raise Exception(
            "No characters found in "
            "config/characters.json"
        )


    return characters


def select_character():

    characters = load_characters()


    character_ids = list(
        characters.keys()
    )


    print(
        "\nAvailable Characters:"
    )


    print(
        "===================="
    )


    for index, character_id in enumerate(
        character_ids,
        start=1
    ):

        character = (
            characters[character_id]
        )


        print(
            f"{index}. "
            f"{character_id} "
            f"({character['name']})"
        )


    while True:

        choice = input(
            "\nSelect character number: "
        )


        try:

            choice = int(choice)


            selected_id = character_ids[
                choice - 1
            ]


            return (
                selected_id,
                characters[selected_id]
            )


        except (
            ValueError,
            IndexError
        ):

            print(
                "Invalid selection."
            )


def get_lora_path(
    character_id,
    character
):

    lora_config = character.get(
        "lora"
    )


    if not lora_config:

        raise Exception(
            f"No LoRA configuration found "
            f"for character: {character_id}"
        )


    lora_path = Path(
        lora_config["path"]
    )


    if not lora_path.is_absolute():

        lora_path = (
            PROJECT_ROOT
            /
            lora_path
        )


    if not lora_path.exists():

        raise FileNotFoundError(
            f"LoRA file not found for "
            f"{character_id}: {lora_path}"
        )


    return lora_path


def get_trigger_word(
    character_id,
    character
):

    lora_config = character.get(
        "lora"
    )


    if not lora_config:

        raise Exception(
            f"No LoRA configuration found "
            f"for character: {character_id}"
        )


    return lora_config.get(
        "trigger_word",
        character_id
    )


def load_model(
    lora_path
):

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )


    torch_dtype = (

        torch.bfloat16
        if device == "cuda"
        else torch.float32

    )


    print(
        "\n[FLUX] Loading base model..."
    )


    print(
        f"[FLUX] Device: {device}"
    )


    print(
        f"[FLUX] Dtype: {torch_dtype}"
    )


    pipe = FluxPipeline.from_pretrained(

        MODEL_NAME,

        torch_dtype=torch_dtype

    )


    print(
        "\n[FLUX] Loading LoRA:"
    )


    print(
        lora_path
    )


    pipe.load_lora_weights(
        str(lora_path)
    )


    if device == "cuda":

        print(
            "\n[FLUX] Enabling sequential CPU offload..."
        )


        pipe.vae.enable_slicing()
        pipe.vae.enable_tiling()


        pipe.enable_sequential_cpu_offload()


    else:

        pipe.to(
            device
        )


    print(
        f"[FLUX] Running on {device}"
    )


    return pipe


def generate_image():

    character_id, character = (
        select_character()
    )


    lora_path = get_lora_path(
        character_id,
        character
    )


    trigger_word = get_trigger_word(
        character_id,
        character
    )


    pipe = load_model(
        lora_path
    )


    print(
        "\nSelected Character:"
    )


    print(
        f"{character_id} "
        f"({character['name']})"
    )


    print(
        "\nSelected LoRA:"
    )


    print(
        lora_path.name
    )


    print(
        "\nTrigger Word:"
    )


    print(
        trigger_word
    )


    print(
        "\nPrompt Example:"
    )


    print(
        "standing in a natural environment, "
        "cinematic lighting"
    )


    user_prompt = input(
        "\nEnter image prompt: "
    )


    full_prompt = (

        f"{trigger_word}, "

        f"{user_prompt} "

    )


    print(
        "\nFinal Prompt:"
    )


    print(
        full_prompt
    )


    width_input = input(
        "\nImage width (default 1024): "
    )


    height_input = input(
        "\nImage height (default 1024): "
    )


    width = (

        int(width_input)
        if width_input
        else 1024

    )


    height = (

        int(height_input)
        if height_input
        else 1024

    )


    steps_input = input(
        "Inference steps (default 4): "
    )


    steps = (

        int(steps_input)
        if steps_input
        else 4

    )


    print(
        "\n[FLUX] Generating..."
    )


    image = pipe(

        prompt=full_prompt,

        width=width,

        height=height,

        num_inference_steps=steps,

        guidance_scale=1.0

    ).images[0]


    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )


    filename = input(
        "\nOutput filename (default image.png): "
    )


    if not filename:

        filename = (
            f"{character_id}.png"
        )


    output = (

        OUTPUT_DIRECTORY
        /
        filename

    )


    image.save(
        output
    )


    print(
        "\nComplete!"
    )


    print(
        f"Saved: {output}"
    )


if __name__ == "__main__":

    generate_image()
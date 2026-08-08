from pathlib import Path

import torch

from diffusers import FluxPipeline


PROJECT_ROOT = Path(__file__).resolve().parent.parent


LORA_DIRECTORY = (
    PROJECT_ROOT
    / "models"
    / "loras"
)


OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "media"
    / "adhoc"
)


MODEL_NAME = (
    "black-forest-labs/FLUX.1-schnell"
)


def find_characters():

    characters = []

    if not LORA_DIRECTORY.exists():
        return characters


    for character_folder in LORA_DIRECTORY.iterdir():

        if not character_folder.is_dir():
            continue


        loras = list(
            character_folder.rglob(
                "*.safetensors"
            )
        )


        if not loras:
            continue


        characters.append(
            {
                "name": character_folder.name,
                "loras": sorted(
                    loras,
                    key=lambda path: path.name
                )
            }
        )


    return characters


def select_character():

    characters = find_characters()


    if not characters:

        raise Exception(
            "No LoRA models found in models/loras/"
        )


    print(
        "\nAvailable Characters:"
    )

    print(
        "===================="
    )


    for index, character in enumerate(
        characters,
        start=1
    ):

        print(
            f"{index}. {character['name']}"
        )


    while True:

        choice = input(
            "\nSelect character number: "
        )


        try:

            choice = int(choice)

            selected = characters[
                choice - 1
            ]

            return selected


        except (
            ValueError,
            IndexError
        ):

            print(
                "Invalid selection."
            )


def select_lora(character):

    loras = character["loras"]


    print(
        "\nAvailable LoRA Versions:"
    )

    print(
        "========================"
    )


    for index, lora in enumerate(
        loras,
        start=1
    ):

        print(
            f"{index}. {lora.stem}"
        )


    while True:

        choice = input(
            "\nSelect LoRA version: "
        )


        try:

            choice = int(choice)

            selected = loras[
                choice - 1
            ]

            return selected


        except (
            ValueError,
            IndexError
        ):

            print(
                "Invalid selection."
            )


def load_model(lora_path):

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


    pipe.to(
        device
    )


    print(
        f"[FLUX] Running on {device}"
    )


    return pipe


def generate_image():

    character = select_character()


    lora_path = select_lora(
        character
    )


    pipe = load_model(
        lora_path
    )


    print(
        "\nSelected Character:"
    )

    print(
        character["name"]
    )


    print(
        "\nSelected LoRA:"
    )

    print(
        lora_path.name
    )


    print(
        "\nPrompt Example:"
    )

    print(
        "standing in a jungle, holding a banana, cinematic lighting"
    )


    user_prompt = input(
        "\nEnter image prompt: "
    )


    full_prompt = (

        f"{character['name']}, "

        f"{user_prompt}, "

        "full body character, "

        "consistent character design, "

        "3D animated movie frame, "

        "cinematic lighting, "

        "expressive pose, "

        "family friendly"

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
        "Image height (default 1024): "
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

        filename = "image.png"


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
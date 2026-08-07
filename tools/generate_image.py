from pathlib import Path
import json
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


def find_loras():

    characters = []

    if not LORA_DIRECTORY.exists():
        return characters


    for character_folder in LORA_DIRECTORY.iterdir():

        if not character_folder.is_dir():
            continue


        loras = list(
            character_folder.glob(
                "*.safetensors"
            )
        )


        for lora in loras:

            characters.append(
                {
                    "name": character_folder.name,
                    "path": lora
                }
            )


    return characters



def select_character():

    characters = find_loras()


    if not characters:
        raise Exception(
            "No LoRA models found in models/loras/"
        )


    print("\nAvailable Characters:")
    print("====================")


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


        except:

            print(
                "Invalid selection."
            )



def load_model(lora_path):

    print("\n[FLUX] Loading base model...")


    pipe = FluxPipeline.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16
    )


    print(
        "[FLUX] Loading LoRA:"
    )

    print(
        lora_path
    )


    pipe.load_lora_weights(
        str(lora_path)
    )


    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
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


    pipe = load_model(
        character["path"]
    )


    print("\nPrompt Example:")
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
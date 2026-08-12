import sys
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__).resolve().parent.parent
)

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


from core.config_loader import ConfigLoader
from core.hardware_detector import HardwareDetector
from characters.character_manager import CharacterManager
from ai.providers.flux_provider import FluxProvider


OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "media"
    / "adhoc"
)


def load_config():

    loader = ConfigLoader()

    config = (
        loader.load_all()
    )

    hardware = (
        HardwareDetector().detect()
    )

    config["hardware"] = hardware

    config["character_manager"] = (
        CharacterManager(
            config["characters"]
        )
    )

    return config


def get_negative_prompt(
    config
):

    active_series = (
        config["series"]["active_series"]
    )

    series_config = (
        config["series"]["series"]
        [active_series]
    )

    image_generation = (
        series_config
        .get(
            "animation_style",
            {}
        )
        .get(
            "image_generation",
            {}
        )
    )

    negative_prompt = (
        image_generation.get(
            "negative_prompt",
            []
        )
    )

    if not isinstance(
        negative_prompt,
        list
    ):

        return ""

    return ", ".join(
        str(item).strip()
        for item in negative_prompt
        if str(item).strip()
    )


def get_available_character_ids(
    character_manager,
    active_series
):

    return (
        character_manager
        .get_character_ids_for_series(
            active_series
        )
    )


def print_available_characters(
    character_manager,
    character_ids
):

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
            character_manager
            .get_character(
                character_id
            )
        )

        print(
            f"{index}. "
            f"{character_id} "
            f"({character.get('name', character_id)})"
        )


def select_scene_characters(
    character_manager,
    character_ids
):

    print_available_characters(
        character_manager,
        character_ids
    )

    print(
        "\nSelect characters for this scene."
    )

    print(
        "Enter numbers separated by commas."
    )

    print(
        "Example: 1,2"
    )

    print(
        "Example: 1,2,3"
    )

    while True:

        choice = input(
            "\nCharacter selection: "
        ).strip()

        if not choice:

            print(
                "Please select at least one character."
            )

            continue

        try:

            selections = [
                int(value.strip())
                for value in choice.split(",")
            ]

            selected_ids = []

            for selection in selections:

                if (
                    selection < 1
                    or
                    selection > len(
                        character_ids
                    )
                ):

                    raise IndexError

                character_id = (
                    character_ids[
                        selection - 1
                    ]
                )

                if character_id not in selected_ids:

                    selected_ids.append(
                        character_id
                    )

            if not selected_ids:

                raise ValueError

            return selected_ids

        except (
            ValueError,
            IndexError
        ):

            print(
                "Invalid selection. "
                "Use character numbers separated by commas."
            )


def get_lora_data(
    character_manager,
    character_ids
):

    lora_paths = []
    lora_strengths = []

    for character_id in character_ids:

        lora_path = (
            character_manager
            .get_lora_path(
                character_id
            )
        )

        strength = (
            character_manager
            .get_lora_strength(
                character_id
            )
        )

        lora_paths.append(
            lora_path
        )

        lora_strengths.append(
            strength
        )

    return (
        lora_paths,
        lora_strengths
    )


def clean_action(
    action
):

    if not isinstance(
        action,
        str
    ):

        return ""

    action = action.strip()

    return action.rstrip(
        ".!?;:, "
    )


def build_character_visual_replacements(
    character_manager,
    character_ids
):

    replacements = []

    for character_id in character_ids:

        trigger_word = (
            character_manager
            .get_trigger_word(
                character_id
            )
        )

        if not trigger_word:

            continue

        character = (
            character_manager
            .get_character(
                character_id
            )
        )

        visual = (
            character.get(
                "visual",
                []
            )
        )

        visual_items = []

        if isinstance(
            visual,
            list
        ):

            visual_items = [
                str(item).strip()
                for item in visual
                if str(item).strip()
            ]

        replacement_parts = [
            trigger_word
        ]

        replacement_parts.extend(
            visual_items
        )

        replacement = (
            ", ".join(
                replacement_parts
            )
            + ","
        )

        replacements.append(
            (
                trigger_word,
                replacement
            )
        )

    return replacements


def build_scene_prompt(
    character_manager,
    character_ids,
    action
):

    action = clean_action(
        action
    )

    if not action:

        return ""

    replacements = (
        build_character_visual_replacements(
            character_manager,
            character_ids
        )
    )

    for (
        trigger_word,
        replacement
    ) in replacements:

        action = action.replace(
            trigger_word,
            replacement
        )

    return action


def print_generation_info(
    episode_character_ids,
    scene_character_ids,
    lora_paths,
    lora_strengths,
    scene_prompt,
    negative_prompt
):

    print(
        "\n=============================="
    )

    print(
        "EPISODE CHARACTERS"
    )

    print(
        episode_character_ids
    )

    print(
        "\nSCENE CHARACTERS"
    )

    print(
        scene_character_ids
    )

    print(
        "\nACTIVE CHARACTER LoRAs"
    )

    for index, character_id in enumerate(
        scene_character_ids
    ):

        print(
            f"{character_id}="
            f"{lora_strengths[index]}"
        )

        print(
            f"  {lora_paths[index]}"
        )

    print(
        "\nFLUX PROMPT"
    )

    print(
        scene_prompt
    )

    print(
        "\nNEGATIVE PROMPT"
    )

    print(
        negative_prompt
    )

    print(
        "==============================\n"
    )


def generate_image():

    config = load_config()

    character_manager = (
        config["character_manager"]
    )

    active_series = (
        config["series"]["active_series"]
    )

    negative_prompt = (
        get_negative_prompt(
            config
        )
    )

    episode_character_ids = (
        get_available_character_ids(
            character_manager,
            active_series
        )
    )

    if not episode_character_ids:

        raise RuntimeError(
            "No characters are available "
            "for the active series."
        )

    print(
        "\n========================================"
    )

    print(
        "MONKI LABS AD-HOC IMAGE GENERATOR"
    )

    print(
        "========================================"
    )

    print(
        f"\nActive Series: "
        f"{active_series}"
    )

    print(
        f"Characters: "
        f"{episode_character_ids}"
    )

    scene_number = 1

    while True:

        print(
            "\n----------------------------------------"
        )

        print(
            f"SCENE TEST {scene_number}"
        )

        print(
            "----------------------------------------"
        )

        scene_character_ids = (
            select_scene_characters(
                character_manager,
                episode_character_ids
            )
        )

        action = input(
            "\nEnter scene action: "
        ).strip()

        if not action:

            print(
                "Scene action cannot be empty."
            )

            continue

        (
            lora_paths,
            lora_strengths
        ) = get_lora_data(
            character_manager,
            scene_character_ids
        )

        print(
            "\nLoading ONLY scene character LoRAs..."
        )

        image_provider = (
            FluxProvider(
                config,
                lora_paths=lora_paths
            )
        )

        image_provider.load_character_loras(
            scene_character_ids,
            lora_paths,
            lora_strengths
        )

        image_provider.set_character_loras(
            scene_character_ids
        )

        scene_prompt = (
            build_scene_prompt(
                character_manager,
                scene_character_ids,
                action
            )
        )

        print_generation_info(
            episode_character_ids,
            scene_character_ids,
            lora_paths,
            lora_strengths,
            scene_prompt,
            negative_prompt
        )

        filename = (
            f"scene_{scene_number:03}.png"
        )

        image_path = (
            image_provider.generate(
                scene_prompt,
                filename,
                OUTPUT_DIRECTORY
            )
        )

        print(
            "\nComplete!"
        )

        print(
            f"Saved: {image_path}"
        )

        scene_number += 1

        print(
            "\nWhat would you like to do next?"
        )

        print(
            "1. Generate another scene"
        )

        print(
            "2. Exit"
        )

        while True:

            next_action = input(
                "\nSelection: "
            ).strip()

            if next_action == "1":

                break

            if next_action == "2":

                print(
                    "\nExiting image generator."
                )

                return

            print(
                "Invalid selection."
            )


if __name__ == "__main__":

    generate_image()
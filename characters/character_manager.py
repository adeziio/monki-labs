from pathlib import Path


class CharacterManager:

    def __init__(
        self,
        characters_config
    ):

        self.characters = (
            characters_config["characters"]
        )


    def get_character(
        self,
        character_id
    ):

        if character_id not in self.characters:

            raise Exception(
                f"Character not found: {character_id}"
            )


        return self.characters[character_id]


    def get_main_character(
        self,
        series_id
    ):

        for character in self.characters.values():

            if (
                character["series"] == series_id
                and
                character["importance"] == "Main"
            ):

                return character


        return None


    def get_main_character_id(
        self,
        series_id
    ):

        for character_id, character in (
            self.characters.items()
        ):

            if (
                character["series"] == series_id
                and
                character["importance"] == "Main"
            ):

                return character_id


        return None


    def get_lora_path(
        self,
        character_id
    ):

        character = self.get_character(
            character_id
        )


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


        if not lora_path.exists():

            raise FileNotFoundError(
                f"LoRA file not found for "
                f"{character_id}: {lora_path}"
            )


        return lora_path


    def get_trigger_word(
        self,
        character_id
    ):

        character = self.get_character(
            character_id
        )


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


    def build_visual_prompt(
        self,
        character
    ):

        appearance = (
            character["appearance"]
        )


        body = (
            appearance["body"]
        )


        face = (
            appearance["face"]
        )


        clothing = ", ".join(

            f'{item["color"]} {item["item"]}'

            for item in appearance["clothing"]

        )


        locked = ", ".join(

            character["visual_consistency"]
            ["locked_features"]

        )


        return (

            f"{character['name']}, "
            f"{character['species']}, "
            f"{body['size']}, "
            f"{body['shape']}, "
            f"{body['fur']}, "
            f"{face['eyes']}, "
            f"{face['expression']}, "
            f"wearing {clothing}, "
            f"consistent appearance: {locked}"

        )


    def build_behavior_prompt(
        self,
        character
    ):

        return ", ".join(

            character.get(
                "behavior_rules",
                []
            )

        )


    def build_story_prompt(
        self,
        character
    ):

        return ", ".join(

            character.get(
                "story_rules",
                []
            )

        )


    def build_complete_prompt(
        self,
        character
    ):

        visual = (
            self.build_visual_prompt(
                character
            )
        )


        behavior = (
            self.build_behavior_prompt(
                character
            )
        )


        return (

            visual
            +
            ". "
            +
            behavior

        )
    
    def get_character_id(
        self,
        character
    ):

        for character_id, stored_character in (
            self.characters.items()
        ):

            if stored_character is character:

                return character_id


        for character_id, stored_character in (
            self.characters.items()
        ):

            if stored_character == character:

                return character_id


        return None


    def get_character_ids_for_series(
        self,
        series_id
    ):

        character_ids = []


        for character_id, character in (
            self.characters.items()
        ):

            if character["series"] == series_id:

                character_ids.append(
                    character_id
                )


        return character_ids
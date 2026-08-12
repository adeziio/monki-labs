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
                character.get("series") == series_id
                and
                character.get("importance") == "Main"
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
                character.get("series") == series_id
                and
                character.get("importance") == "Main"
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


    def get_lora_strength(
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

        strength = lora_config.get(
            "strength",
            1.0
        )

        try:

            strength = float(
                strength
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                f"Invalid LoRA strength for "
                f"{character_id}: {strength}"
            )

        if strength < 0:

            raise ValueError(
                f"LoRA strength cannot be negative "
                f"for {character_id}: {strength}"
            )

        return strength


    def get_visual_features(
        self,
        character_id
    ):

        character = self.get_character(
            character_id
        )

        visual = character.get(
            "visual",
            []
        )

        if not isinstance(
            visual,
            list
        ):

            return []

        return [
            str(item).strip()
            for item in visual
            if str(item).strip()
        ]


    def get_personality(
        self,
        character_id
    ):

        character = self.get_character(
            character_id
        )

        personality = character.get(
            "personality",
            []
        )

        if not isinstance(
            personality,
            list
        ):

            return []

        return [
            str(item).strip()
            for item in personality
            if str(item).strip()
        ]


    def get_behavior_rules(
        self,
        character_id
    ):

        character = self.get_character(
            character_id
        )

        rules = character.get(
            "behavior_rules",
            []
        )

        if not isinstance(
            rules,
            list
        ):

            return []

        return [
            str(item).strip()
            for item in rules
            if str(item).strip()
        ]


    def get_story_rules(
        self,
        character_id
    ):

        character = self.get_character(
            character_id
        )

        rules = character.get(
            "story_rules",
            []
        )

        if not isinstance(
            rules,
            list
        ):

            return []

        return [
            str(item).strip()
            for item in rules
            if str(item).strip()
        ]


    def build_visual_prompt(
        self,
        character_id
    ):

        trigger_word = (
            self.get_trigger_word(
                character_id
            )
        )

        if not trigger_word:

            return ""

        return trigger_word


    def build_behavior_prompt(
        self,
        character_id
    ):

        return ", ".join(
            self.get_behavior_rules(
                character_id
            )
        )


    def build_story_prompt(
        self,
        character_id
    ):

        return ", ".join(
            self.get_story_rules(
                character_id
            )
        )


    def build_complete_prompt(
        self,
        character_id
    ):

        visual = (
            self.build_visual_prompt(
                character_id
            )
        )

        behavior = (
            self.build_behavior_prompt(
                character_id
            )
        )

        parts = []

        if visual:

            parts.append(
                visual
            )

        if behavior:

            parts.append(
                behavior
            )

        return ". ".join(
            parts
        )


    def get_character_ids_for_series(
        self,
        series_id
    ):

        character_ids = []

        for character_id, character in (
            self.characters.items()
        ):

            if character.get("series") == series_id:

                character_ids.append(
                    character_id
                )

        return character_ids
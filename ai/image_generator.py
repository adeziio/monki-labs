from ai.base_ai_service import BaseAIService
from ai.providers.flux_provider import FluxProvider


class ImageGenerator(BaseAIService):

    def __init__(
        self,
        config
    ):

        super().__init__(
            config
        )

        self.config = config

        self.character_manager = (
            config["character_manager"]
        )

        self.active_series = (
            config["series"]["active_series"]
        )

        self.series_config = (
            config["series"]["series"]
            [self.active_series]
        )

        image_generation = (
            self.series_config
            .get(
                "animation_style",
                {}
            )
            .get(
                "image_generation",
                {}
            )
        )

        self.negative_prompt = ", ".join(
            image_generation.get(
                "negative_prompt",
                []
            )
        )

        self.image_provider = None


    def build_character_prompt(
        self,
        character_ids
    ):

        character_parts = []

        for character_id in character_ids:

            trigger_word = (
                self.character_manager
                .get_trigger_word(
                    character_id
                )
            )

            if not trigger_word:

                continue

            visual = (
                self.character_manager
                .get_character(
                    character_id
                )
                .get(
                    "visual",
                    []
                )
            )

            parts = [
                trigger_word
            ]

            if isinstance(
                visual,
                list
            ):

                parts.extend(
                    str(item).strip()
                    for item in visual
                    if str(item).strip()
                )

            character_parts.append(
                ", ".join(parts)
            )

        return ", ".join(
            character_parts
        )


    def get_lora_paths(
        self,
        character_ids
    ):

        lora_paths = []

        for character_id in character_ids:

            lora_path = (
                self.character_manager
                .get_lora_path(
                    character_id
                )
            )

            lora_paths.append(
                lora_path
            )

        return lora_paths


    def get_lora_strengths(
        self,
        character_ids
    ):

        strengths = []

        for character_id in character_ids:

            strength = (
                self.character_manager
                .get_lora_strength(
                    character_id
                )
            )

            strengths.append(
                strength
            )

        return strengths


    def clean_action(
        self,
        action
    ):

        if not isinstance(
            action,
            str
        ):

            return ""

        action = action.strip()

        action = action.rstrip(
            ".!?;:, "
        )

        return action


    def get_scene_character_ids(
        self,
        scene,
        all_character_ids
    ):

        action = scene.get(
            "action",
            ""
        )

        if not action:

            return []

        action_lower = action.lower()

        scene_character_ids = []

        for character_id in all_character_ids:

            trigger_word = (
                self.character_manager
                .get_trigger_word(
                    character_id
                )
            )

            if not trigger_word:

                continue

            if (
                trigger_word.lower()
                in action_lower
            ):

                scene_character_ids.append(
                    character_id
                )

        return scene_character_ids


    def build_character_visual_replacements(
        self,
        character_ids
    ):

        replacements = []

        for character_id in character_ids:

            trigger_word = (
                self.character_manager
                .get_trigger_word(
                    character_id
                )
            )

            if not trigger_word:

                continue

            visual = (
                self.character_manager
                .get_character(
                    character_id
                )
                .get(
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


    def build_image_prompt(
        self,
        character_ids,
        scene
    ):

        action = self.clean_action(
            scene.get(
                "action",
                ""
            )
        )

        if not action:

            return ""

        replacements = (
            self.build_character_visual_replacements(
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


    def generate(
        self,
        story,
        episode
    ):

        self.log(
            "Generating scene images"
        )

        generated_scenes = []

        self.image_provider = (
            FluxProvider(
                self.config
            )
        )

        characters = story.get(
            "characters",
            {}
        )

        if isinstance(
            characters,
            dict
        ):

            all_character_ids = list(
                characters.keys()
            )

        else:

            all_character_ids = []

        if not all_character_ids:

            main_character_id = (
                self.character_manager
                .get_main_character_id(
                    self.active_series
                )
            )

            if main_character_id:

                all_character_ids = [
                    main_character_id
                ]

        all_lora_paths = (
            self.get_lora_paths(
                all_character_ids
            )
        )

        all_lora_strengths = (
            self.get_lora_strengths(
                all_character_ids
            )
        )

        self.image_provider.load_character_loras(
            all_character_ids,
            all_lora_paths,
            all_lora_strengths
        )

        for index, scene in enumerate(
            story["scenes"],
            start=1
        ):

            scene_character_ids = (
                self.get_scene_character_ids(
                    scene,
                    all_character_ids
                )
            )

            if not scene_character_ids:

                scene_character_ids = [
                    all_character_ids[0]
                ]

            self.image_provider.set_character_loras(
                scene_character_ids
            )

            scene_prompt = (
                self.build_image_prompt(
                    scene_character_ids,
                    scene
                )
            )

            print(
                "\n=============================="
            )

            print(
                "EPISODE CHARACTERS"
            )

            print(
                all_character_ids
            )

            print(
                "\nSCENE CHARACTERS"
            )

            print(
                scene_character_ids
            )

            print(
                "\nFLUX PROMPT"
            )

            print(
                scene_prompt
            )

            print(
                "==============================\n"
            )

            filename = (
                f"scene_{index:03}.png"
            )

            image_path = (
                self.image_provider.generate(
                    scene_prompt,
                    filename,
                    episode.get_path()
                    /
                    "scenes"
                )
            )

            generated_scenes.append(
                {
                    "scene": index,
                    "characters":
                        scene_character_ids,
                    "image": image_path
                }
            )

        return generated_scenes
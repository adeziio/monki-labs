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


        series_config = (
            config["series"]["series"]
            [self.active_series]
        )


        image_generation = (
            series_config
            ["animation_style"]
            ["image_generation"]
        )


        self.style_prompt = ", ".join(
            image_generation["style_prompt"]
        )


        self.negative_prompt = ", ".join(
            image_generation["negative_prompt"]
        )


        self.image_provider = None


    def build_character_prompt(
        self,
        character_ids
    ):

        trigger_words = []


        for character_id in character_ids:

            character = (
                self.character_manager
                .get_character(
                    character_id
                )
            )


            trigger_word = (
                self.character_manager
                .get_trigger_word(
                    character_id
                )
            )


            trigger_words.append(
                trigger_word
            )


        return ", ".join(
            trigger_words
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


    def generate(
        self,
        storyboard,
        episode
    ):

        self.log(
            "Generating scene images"
        )


        generated_scenes = []


        for index, scene in enumerate(

            storyboard["scenes"],

            start=1

        ):

            character_ids = (
                scene.get(
                    "characters",
                    []
                )
            )


            if not character_ids:

                character_ids = [
                    self.character_manager
                    .get_main_character_id(
                        self.active_series
                    )
                ]


            lora_paths = (
                self.get_lora_paths(
                    character_ids
                )
            )


            self.image_provider = (
                FluxProvider(
                    self.config,
                    lora_paths=lora_paths
                )
            )


            trigger_words = (
                self.build_character_prompt(
                    character_ids
                )
            )


            scene_prompt = (

                f"{trigger_words}, "

                f"{scene['description']}. "

                f"{self.style_prompt}. "

            )


            print(
                "\n=============================="
            )


            print(
                "SCENE CHARACTERS"
            )


            print(
                character_ids
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
                    "characters": character_ids,
                    "image": image_path
                }

            )


        return generated_scenes
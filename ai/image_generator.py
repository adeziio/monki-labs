from ai.base_ai_service import BaseAIService
from ai.providers.stable_diffusion_provider import StableDiffusionProvider


class ImageGenerator(BaseAIService):


    def __init__(self, config):

        super().__init__(config)


        self.character_manager = (
            config["character_manager"]
        )


        self.image_provider = (
            StableDiffusionProvider(
                config
            )
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

            image_generation[
                "style_prompt"
            ]

        )


        self.negative_prompt = ", ".join(

            image_generation[
                "negative_prompt"
            ]

        )



    def shorten_prompt(
        self,
        prompt,
        max_words=70
    ):


        words = prompt.split()


        if len(words) <= max_words:

            return prompt


        return " ".join(

            words[:max_words]

        )



    def generate(
        self,
        storyboard,
        episode
    ):


        self.log(
            "Generating scene images"
        )


        character = (

            self.character_manager
            .get_main_character(
                self.active_series
            )

        )


        character_prompt = (

            self.character_manager
            .build_visual_prompt(
                character
            )

        )


        generated_scenes = []


        for index, scene in enumerate(

            storyboard["scenes"],
            start=1

        ):


            scene_prompt = (

                f"{character_prompt}. "

                f"{scene['description']}. "

                f"{self.style_prompt}. "

                "Full body character, "
                "centered composition, "
                "character completely visible."

            )


            scene_prompt = (

                self.shorten_prompt(
                    scene_prompt
                )

            )


            print(
                "\n=============================="
            )

            print(
                "IMAGE GENERATION PROMPT"
            )

            print(
                "=============================="
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

                    self.negative_prompt,

                    filename,

                    episode.get_path()
                    /
                    "scenes"

                )

            )


            generated_scenes.append(

                {

                    "scene":
                    index,

                    "image":
                    image_path

                }

            )


        return generated_scenes
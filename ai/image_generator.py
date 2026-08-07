from ai.base_ai_service import BaseAIService
from ai.providers.stable_diffusion_provider import StableDiffusionProvider

from characters.reference_loader import CharacterReferenceLoader



class ImageGenerator(BaseAIService):


    def __init__(self, config):

        super().__init__(
            config
        )


        self.character_manager = (
            config["character_manager"]
        )


        self.reference_loader = (
            CharacterReferenceLoader(
                "characters/references/max_the_monkey"
            )
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



    def generate(
        self,
        storyboard,
        episode
    ):


        self.log(
            "Generating scene images"
        )


        reference_images = (
            self.reference_loader
            .get_reference_images()
        )


        main_reference = (
            reference_images[0]
        )


        generated_scenes = []


        for index, scene in enumerate(

            storyboard["scenes"],

            start=1

        ):


            scene_prompt = (

                f"Create this animation scene: "
                f"{scene['description']}. "

                f"{self.style_prompt}. "

                "Keep the exact same character identity, "
                "same face, same fur, same clothing. "

                "Full body, centered composition."

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
                    "scenes",

                    main_reference

                )

            )


            generated_scenes.append(

                {
                    "scene": index,
                    "image": image_path
                }

            )


        return generated_scenes
from ai.base_ai_service import BaseAIService
from ai.providers.stable_diffusion_provider import StableDiffusionProvider

from characters.reference_loader import CharacterReferenceLoader



class ImageGenerator(BaseAIService):


    def __init__(self, config):

        super().__init__(config)


        self.character_loader = (
            CharacterReferenceLoader(
                "characters/references/max_the_monkey"
            )
        )


        self.image_provider = (
            StableDiffusionProvider(
                config
            )
        )



    def generate(self, storyboard, episode):


        self.log(
            "Generating scene images"
        )


        character_prompt = (
            self.character_loader
            .build_prompt()
        )


        reference_images = (
            self.character_loader
            .get_reference_images()
        )


        generated_scenes = []


        for index, scene in enumerate(
            storyboard["scenes"],
            start=1
        ):


            prompt = (

                character_prompt

                +

                "\nScene:\n"

                +

                str(
                    scene["description"]
                )

            )


            filename = (
                f"scene_{index:03}.png"
            )


            image_path = (
                self.image_provider.generate(
                    prompt,
                    filename,
                    episode.get_path() / "scenes"
                )
            )


            generated_scenes.append(

                {

                    "scene":
                    index,

                    "image":
                    image_path,

                    "reference_images":
                    reference_images

                }

            )


        return generated_scenes
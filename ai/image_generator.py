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


        self.image_provider = FluxProvider(
            config
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


            scene_prompt = (

                "maxmonkey, "

                "Max the monkey character, "

                "cute cartoon monkey, "

                "blue hoodie, "

                "red baseball cap, "

                "consistent character design, "

                "same face, "

                "same fur pattern, "

                "same clothing, "

                "full body character, "

                f"{scene['description']}. "

                f"{self.style_prompt}. "

                "3D animated movie frame, "

                "cinematic lighting, "

                "expressive pose, "

                "family friendly."

            )


            print(
                "\n=============================="
            )

            print(
                "FLUX PROMPT"
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
                    "scene": index,
                    "image": image_path
                }

            )


        return generated_scenes
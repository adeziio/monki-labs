from pathlib import Path

from ai.base_ai_service import BaseAIService

from ai.providers.animation_provider import AnimationProvider





class AnimationGenerator(BaseAIService):


    def __init__(
        self,
        config
    ):


        super().__init__(
            config
        )


        device = (
            config["hardware"]["device"]
        )


        self.provider = (
            AnimationProvider(
                config,
                device
            )
        )



    def generate(
        self,
        scenes,
        episode
    ):


        self.log(
            "Generating animated scenes"
        )


        animations = []


        output_directory = (
            episode.get_path()
            /
            "video"
        )


        output_directory.mkdir(
            parents=True,
            exist_ok=True
        )



        for scene in scenes:


            scene_number = (
                scene["scene"]
            )


            image_path = Path(
                scene["image"]
            )


            output_file = (
                output_directory
                /
                f"scene_{scene_number:03}.mp4"
            )


            video_path = (
                self.provider.generate(
                    image_path,
                    output_file
                )
            )


            animations.append(

                {

                    "scene":
                    scene_number,

                    "image":
                    str(image_path),

                    "video":
                    video_path,

                    "animation_status":
                    "complete"

                }

            )


        return animations
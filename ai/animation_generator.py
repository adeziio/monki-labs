from ai.base_ai_service import BaseAIService

from pathlib import Path

from moviepy import ImageClip



class AnimationGenerator(BaseAIService):


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


            clip = (
                ImageClip(
                    str(image_path)
                )
                .with_duration(3)
            )


            clip.write_videofile(
                str(output_file),
                fps=24,
                codec="libx264",
                audio=False
            )


            animations.append(

                {

                    "scene":
                    scene_number,

                    "image":
                    str(image_path),

                    "video":
                    str(output_file),

                    "animation_status":
                    "complete"

                }

            )


        return animations
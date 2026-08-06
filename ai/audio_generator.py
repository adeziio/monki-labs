from ai.base_ai_service import BaseAIService

from pathlib import Path
import random



class AudioGenerator(BaseAIService):


    def __init__(self, config):

        super().__init__(config)


        self.audio_rules = (
            config["audio"]
            ["audio_rules"]
        )


        self.music_directory = Path(
            self.audio_rules["music"]["directory"]
        )



    def generate(self, animations):


        self.log(
            "Generating audio plan"
        )


        music_file = None


        if self.audio_rules["music"]["enabled"]:


            music_files = list(
                self.music_directory.glob(
                    "*.mp3"
                )
            )


            if music_files:

                music_file = str(
                    random.choice(
                        music_files
                    )
                )

            print(
                f"Selected music: {music_file}"
            )



        return {


            "music":

            music_file,


            "sound_effects":

            [],


            "dialogue":

            False,


            "voice":

            False

        }
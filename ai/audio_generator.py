from ai.base_ai_service import BaseAIService



class AudioGenerator(BaseAIService):


    def generate(self, scenes):


        self.log(
            "Generating audio plan"
        )


        return {


            "music":

            "cartoon_comedy",


            "sound_effects":

            [

                "footsteps",

                "impact",

                "environment"

            ]

        }
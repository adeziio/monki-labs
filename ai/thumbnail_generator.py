from ai.base_ai_service import BaseAIService



class ThumbnailGenerator(BaseAIService):


    def generate(self, episode):


        self.log(
            "Generating thumbnail"
        )


        return {


            "thumbnail":

            "best_funny_scene"


        }
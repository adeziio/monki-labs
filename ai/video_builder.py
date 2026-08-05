from ai.base_ai_service import BaseAIService



class VideoBuilder(BaseAIService):


    def build(
        self,
        animations,
        audio
    ):


        self.log(
            "Building final video"
        )


        return {

            "output":

            "media/output/episode.mp4"

        }
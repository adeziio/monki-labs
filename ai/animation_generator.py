from ai.base_ai_service import BaseAIService



class AnimationGenerator(BaseAIService):


    def generate(self, scenes):


        self.log(
            "Preparing animation scenes"
        )


        animations = []


        for scene in scenes:


            animations.append(

                {


                    "scene":

                    scene["scene"],


                    "animation_status":

                    "ready"


                }

            )


        return animations
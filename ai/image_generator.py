from ai.base_ai_service import BaseAIService



class ImageGenerator(BaseAIService):


    def generate(self, storyboard):


        self.log(
            "Generating scene prompts"
        )


        scenes = []


        for scene in storyboard["scenes"]:


            scenes.append(

                {


                    "scene":

                    scene["scene"],


                    "prompt":

                    scene["description"],


                    "reference_required":

                    True


                }

            )


        return scenes
from ai.base_ai_service import BaseAIService
from characters.reference_loader import CharacterReferenceLoader



class ImageGenerator(BaseAIService):


    def __init__(self, config):

        super().__init__(config)


        self.character_loader = (
            CharacterReferenceLoader(
                "characters/references/max_the_monkey"
            )
        )



    def generate(self, storyboard):


        self.log(
            "Generating scene prompts"
        )


        character_prompt = (
            self.character_loader
            .build_prompt()
        )


        reference_images = (
            self.character_loader
            .get_reference_images()
        )

        print(
            "Character references:",
            reference_images
        )


        scenes = []


        for scene in storyboard["scenes"]:


            scenes.append(

                {


                    "scene":

                    scene["scene"],


                    "prompt":

                    character_prompt
                    +
                    "\nScene:\n"
                    +
                    str(scene["description"]),


                    "reference_images":

                    reference_images,


                    "reference_required":

                    True


                }

            )


        return scenes
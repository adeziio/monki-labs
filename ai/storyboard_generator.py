from ai.base_ai_service import BaseAIService



class StoryboardGenerator(BaseAIService):


    def generate(self, story):


        self.log(
            "Creating storyboard"
        )


        return {


            "scenes": [

                {

                    "scene": 1,

                    "purpose": "Hook",

                    "description":
                    story["hook"]

                },


                {

                    "scene": 2,

                    "purpose": "Setup",

                    "description":
                    story["setup"]

                },


                {

                    "scene": 3,

                    "purpose": "Escalation",

                    "description":
                    story["escalation"]

                },


                {

                    "scene": 4,

                    "purpose": "Ending",

                    "description":
                    story["ending"]

                }


            ]

        }
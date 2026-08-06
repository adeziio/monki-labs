from ai.base_ai_service import BaseAIService



class StoryboardGenerator(BaseAIService):


    def normalize_description(self, value):


        if isinstance(value, list):

            return " ".join(value)


        return str(value)



    def generate(self, story):


        self.log(
            "Creating storyboard"
        )


        scenes = [

            {
                "scene": 1,

                "purpose": "Hook",

                "description":
                self.normalize_description(
                    story.get(
                        "hook",
                        "Max discovers something interesting"
                    )
                )

            },


            {
                "scene": 2,

                "purpose": "Setup",

                "description":
                self.normalize_description(
                    story.get(
                        "setup",
                        "Max explores the situation"
                    )
                )

            },


            {
                "scene": 3,

                "purpose": "Escalation",

                "description":
                self.normalize_description(
                    story.get(
                        "escalation",
                        "Things become chaotic"
                    )
                )

            },


            {
                "scene": 4,

                "purpose": "Ending",

                "description":
                self.normalize_description(
                    story.get(
                        "ending",
                        "A funny surprise happens"
                    )
                )

            }

        ]


        return {

            "scenes": scenes

        }
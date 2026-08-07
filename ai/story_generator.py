import json

from ai.base_ai_service import BaseAIService
from ai.providers.ollama_provider import OllamaProvider



class StoryGenerator(BaseAIService):


    def __init__(
        self,
        config
    ):

        super().__init__(
            config
        )


        self.llm = OllamaProvider(
            config
        )


        self.character_manager = (
            config["character_manager"]
        )


        self.active_series = (
            config["series"]["active_series"]
        )



    def generate(self):


        self.log(
            "Generating episode idea"
        )


        character = (
            self.character_manager
            .get_main_character(
                self.active_series
            )
        )


        character_prompt = (

            self.character_manager
            .build_story_prompt(
                character
            )

        )


        visual_identity = (

            self.character_manager
            .build_visual_prompt(
                character
            )

        )


        prompt = f"""

            Create a silent animated cartoon episode.

            Main character:

            {visual_identity}


            Character rules:

            {character_prompt}


            IMPORTANT:

            - The main character must always be Max.
            - Max is a monkey.
            - Do not create a new main character.
            - Do not replace Max with another animal.
            - Do not introduce a different protagonist.
            - Max never speaks.
            - Max communicates only through actions, expressions, and physical comedy.


            Episode rules:

            - No dialogue
            - No narration
            - Family friendly
            - Physical comedy only
            - Classic cartoon timing
            - Funny visual storytelling
            - The story must be understandable without words


            Return ONLY valid JSON.

            Format:

            {{
                "concept": "",
                "hook": "",
                "setup": "",
                "escalation": "",
                "ending": ""
            }}

        """


        response = self.llm.generate(
            prompt
        )


        return self.parse_response(
            response
        )



    def parse_response(
        self,
        response
    ):


        required_fields = {


            "concept":
            "Max discovers something strange",


            "hook":
            "Max finds something unexpected",


            "setup":
            "Max investigates the situation",


            "escalation":
            "The situation becomes chaotic",


            "ending":
            "A funny surprise happens"


        }



        try:


            data = json.loads(
                response
            )


            for key, fallback in required_fields.items():


                if key not in data or not data[key]:

                    data[key] = fallback



            return data



        except json.JSONDecodeError:


            self.log(
                "AI returned invalid JSON. Using fallback."
            )


            return required_fields
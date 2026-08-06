import json

from ai.base_ai_service import BaseAIService
from ai.providers.ollama_provider import OllamaProvider



class StoryGenerator(BaseAIService):


    def __init__(self, config):

        super().__init__(config)

        self.llm = OllamaProvider(
            config
        )



    def generate(self):


        self.log(
            "Generating episode idea"
        )


        prompt = """

            Create a silent animated cartoon episode.

            Rules:

            - No dialogue
            - No narration
            - Family friendly
            - Physical comedy only
            - Main character communicates through actions
            - Inspired by classic cartoon timing

            Return ONLY valid JSON.

            Format:

            {
                "concept": "",
                "hook": "",
                "setup": "",
                "escalation": "",
                "ending": ""
            }

        """


        response = self.llm.generate(
            prompt
        )


        return self.parse_response(
            response
        )



    def parse_response(self, response):

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

            data = json.loads(response)


            for key, fallback in required_fields.items():

                if key not in data or not data[key]:

                    data[key] = fallback


            return data



        except json.JSONDecodeError:


            self.log(
                "AI returned invalid JSON. Using fallback."
            )


            return required_fields
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


        try:

            return json.loads(
                response
            )


        except json.JSONDecodeError:


            self.log(
                "AI returned invalid JSON. Using fallback."
            )


            return {


                "concept":
                "Max discovers something strange",


                "hook":
                "Max finds a mysterious object",


                "setup":
                "Max tries to understand it",


                "escalation":
                "The situation becomes chaotic",


                "ending":
                "Max discovers a funny surprise"

            }
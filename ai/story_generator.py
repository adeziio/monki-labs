from ai.base_ai_service import BaseAIService
from ai.providers.ollama_provider import OllamaProvider



class StoryGenerator(BaseAIService):


    def __init__(self, config):

        super().__init__(config)

        self.llm = OllamaProvider(
            config
        )



    def generate(self):


        prompt = """

Create a silent animated cartoon episode.

Rules:

- No dialogue
- No narration
- Main character communicates through actions
- Family friendly
- Physical comedy

Create:

1. Hook
2. Setup
3. Escalation
4. Twist ending

Return JSON.

"""


        response = self.llm.generate(
            prompt
        )


        return response
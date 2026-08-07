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

Create a silent animated cartoon episode idea.

Main character:

{visual_identity}


Character rules:

{character_prompt}


Important rules:

- The main character must always be Max.
- Max is a monkey.
- Max never speaks.
- Max communicates through actions, expressions, and physical comedy.


Episode rules:

- No dialogue.
- No narration.
- Family friendly.
- Physical comedy only.
- Classic cartoon timing.
- The story must work without words.


IMPORTANT OUTPUT RULES:

Return ONLY valid JSON.

Do NOT create scenes.
Do NOT create frames.
Do NOT create images.
Do NOT create captions.
Do NOT create lists.
Do NOT create nested objects.

Each field must be a single short sentence.

Required format:

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
            "Max discovers something strange.",


            "hook":
            "Max finds something unexpected.",


            "setup":
            "Max investigates the situation.",


            "escalation":
            "The situation becomes chaotic.",


            "ending":
            "A funny surprise happens."

        }



        try:


            data = json.loads(
                response
            )


            cleaned = {}


            for key, fallback in required_fields.items():


                value = data.get(
                    key,
                    fallback
                )


                if isinstance(
                    value,
                    str
                ):

                    cleaned[key] = value


                else:

                    cleaned[key] = self.extract_text(
                        value,
                        fallback
                    )


            return cleaned



        except json.JSONDecodeError:


            self.log(
                "AI returned invalid JSON. Using fallback."
            )


            return required_fields



    def extract_text(
        self,
        value,
        fallback
    ):


        if isinstance(
            value,
            dict
        ):


            if "description" in value:

                return str(
                    value["description"]
                )


            if "scene" in value:

                return self.extract_text(
                    value["scene"],
                    fallback
                )



        if isinstance(
            value,
            list
        ):


            results = []


            for item in value:

                text = self.extract_text(
                    item,
                    ""
                )


                if text:

                    results.append(
                        text
                    )


            if results:

                return ". ".join(
                    results
                )



        return fallback
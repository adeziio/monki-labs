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


        main_character = (
            self.character_manager
            .get_main_character(
                self.active_series
            )
        )


        character_ids = (
            self.character_manager
            .get_character_ids_for_series(
                self.active_series
            )
        )


        character_descriptions = []


        for character_id in character_ids:

            character = (
                self.character_manager
                .get_character(
                    character_id
                )
            )


            visual_identity = (
                self.character_manager
                .build_visual_prompt(
                    character
                )
            )


            character_descriptions.append(

                f"- {character_id}: "
                f"{visual_identity}"

            )


        characters_prompt = "\n".join(
            character_descriptions
        )


        main_character_id = (
            self.character_manager
            .get_character_id(
                main_character
            )
        )


        prompt = f"""
            Create a silent animated cartoon episode idea.

            Available characters:

            {characters_prompt}

            Main character:
            {main_character_id}

            Character rules:

            - Characters never speak.
            - Characters never use dialogue.
            - Characters communicate through movement and facial expressions.
            - Humor comes from physical comedy, reactions, timing, and visual situations.
            - Characters must retain their established visual identities.

            Episode rules:

            - Max must appear in every episode.
            - Other characters may appear when they improve the story.
            - Use only characters from the available character list.
            - No dialogue.
            - No narration.
            - Family friendly.
            - Physical comedy only.
            - Classic cartoon timing.
            - The story must work completely without words.

            IMPORTANT OUTPUT RULES:

            Return ONLY valid JSON.

            Do NOT create scenes.
            Do NOT create frames.
            Do NOT create images.
            Do NOT create captions.
            Do NOT create nested objects.

            The "characters" field must contain character IDs from the available character list.

            Each field must be a single short sentence.

            Required format:

            {{
            "concept": "",
            "hook": "",
            "setup": "",
            "escalation": "",
            "ending": "",
            "characters": ["{main_character_id}"]
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

        main_character_id = (
            self.character_manager
            .get_main_character_id(
                self.active_series
            )
        )


        required_fields = {

            "concept":
            "The main character discovers something strange.",

            "hook":
            "The main character encounters something unexpected.",

            "setup":
            "The characters investigate the situation.",

            "escalation":
            "The situation becomes increasingly chaotic.",

            "ending":
            "A funny visual surprise ends the adventure.",

            "characters": [
                main_character_id
            ]

        }


        try:

            data = json.loads(
                response
            )


            cleaned = {}


            for key, fallback in (
                required_fields.items()
            ):

                value = data.get(
                    key,
                    fallback
                )


                if key == "characters":

                    if isinstance(
                        value,
                        list
                    ):

                        valid_characters = []

                        for character_id in value:

                            if (
                                character_id
                                in self.character_manager.characters
                            ):

                                character = (
                                    self.character_manager
                                    .get_character(
                                        character_id
                                    )
                                )


                                if (
                                    character["series"]
                                    ==
                                    self.active_series
                                ):

                                    valid_characters.append(
                                        character_id
                                    )


                        if main_character_id not in (
                            valid_characters
                        ):

                            valid_characters.insert(
                                0,
                                main_character_id
                            )


                        cleaned[key] = (
                            valid_characters
                        )

                    else:

                        cleaned[key] = (
                            fallback
                        )


                elif isinstance(
                    value,
                    str
                ):

                    cleaned[key] = value


                else:

                    cleaned[key] = (
                        self.extract_text(
                            value,
                            fallback
                        )
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
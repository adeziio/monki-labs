from ai.base_ai_service import BaseAIService


class StoryboardGenerator(BaseAIService):

    def __init__(
        self,
        config
    ):

        super().__init__(
            config
        )


        self.character_manager = (
            config["character_manager"]
        )


        self.active_series = (
            config["series"]["active_series"]
        )


    def normalize_description(
        self,
        value
    ):

        if isinstance(
            value,
            str
        ):

            return value


        if isinstance(
            value,
            dict
        ):

            if "description" in value:

                return str(
                    value["description"]
                )


            if "scene" in value:

                return self.normalize_description(
                    value["scene"]
                )


        if isinstance(
            value,
            list
        ):

            descriptions = []


            for item in value:

                text = self.normalize_description(
                    item
                )


                if text:

                    descriptions.append(
                        text
                    )


            return ". ".join(
                descriptions
            )


        return str(
            value
        )


    def normalize_characters(
        self,
        characters
    ):

        if not isinstance(
            characters,
            list
        ):

            characters = []


        valid_characters = []


        for character_id in characters:

            try:

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


            except Exception:

                continue


        main_character_id = (
            self.character_manager
            .get_main_character_id(
                self.active_series
            )
        )


        if (
            main_character_id
            and
            main_character_id
            not in valid_characters
        ):

            valid_characters.insert(
                0,
                main_character_id
            )


        return valid_characters


    def generate(
        self,
        story
    ):

        self.log(
            "Creating storyboard"
        )


        characters = (
            self.normalize_characters(
                story.get(
                    "characters",
                    []
                )
            )
        )


        scenes = [

            {
                "scene": 1,
                "purpose": "Hook",
                "characters": characters,
                "description":
                self.normalize_description(
                    story.get(
                        "hook",
                        "The main character encounters something interesting"
                    )
                )
            },

            {
                "scene": 2,
                "purpose": "Setup",
                "characters": characters,
                "description":
                self.normalize_description(
                    story.get(
                        "setup",
                        "The characters explore the situation"
                    )
                )
            },

            {
                "scene": 3,
                "purpose": "Escalation",
                "characters": characters,
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
                "characters": characters,
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
            "characters": characters,
            "scenes": scenes
        }
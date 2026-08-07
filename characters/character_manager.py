class CharacterManager:


    def __init__(self, characters_config):

        self.characters = (
            characters_config["characters"]
        )



    def get_character(
        self,
        character_id
    ):

        if character_id not in self.characters:

            raise Exception(
                f"Character not found: {character_id}"
            )

        return (
            self.characters[
                character_id
            ]
        )



    def get_main_character(
        self,
        series_id
    ):

        for character in self.characters.values():

            if (
                character["series"] == series_id
                and
                character["importance"] == "Main"
            ):

                return character

        return None



    def build_visual_prompt(
        self,
        character
    ):


        appearance = (
            character["appearance"]
        )


        body = (
            appearance["body"]
        )


        face = (
            appearance["face"]
        )


        clothing = ", ".join(

            f'{item["color"]} {item["item"]}'

            for item in appearance["clothing"]

        )


        prompt = (

            f'{character["name"]}, '

            f'{character["species"]}, '

            f'{body["size"]}, '

            f'{body["shape"]}, '

            f'{body["fur"]}, '

            f'{face["eyes"]}, '

            f'{face["expression"]}, '

            f'wearing {clothing}'

        )


        return prompt



    def build_behavior_prompt(
        self,
        character
    ):


        return ", ".join(

            character[
                "behavior_rules"
            ]

        )



    def build_story_prompt(
        self,
        character
    ):


        return ", ".join(

            character[
                "story_rules"
            ]

        )



    def build_complete_prompt(
        self,
        character
    ):


        return (

            self.build_visual_prompt(
                character
            )

            +

            ". "

            +

            self.build_behavior_prompt(
                character
            )

        )
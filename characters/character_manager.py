class CharacterManager:


    def __init__(
        self,
        characters_config
    ):

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


        return self.characters[character_id]



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


        locked = ", ".join(

            character["visual_consistency"]
            ["locked_features"]

        )


        return (

            f"{character['name']}, "
            f"{character['species']}, "
            f"{body['size']}, "
            f"{body['shape']}, "
            f"{body['fur']}, "
            f"{face['eyes']}, "
            f"{face['expression']}, "
            f"wearing {clothing}, "
            f"consistent appearance: {locked}"

        )



    def build_behavior_prompt(
        self,
        character
    ):


        return ", ".join(

            character.get(
                "behavior_rules",
                []
            )

        )



    def build_story_prompt(
        self,
        character
    ):


        return ", ".join(

            character.get(
                "story_rules",
                []
            )

        )



    def build_complete_prompt(
        self,
        character
    ):


        visual = (
            self.build_visual_prompt(
                character
            )
        )


        behavior = (
            self.build_behavior_prompt(
                character
            )
        )


        return (

            visual

            +

            ". "

            +

            behavior

        )



    def get_reference_images(
        self,
        character
    ):


        visual_consistency = (
            character.get(
                "visual_consistency",
                {}
            )
        )


        reference_folder = (
            visual_consistency.get(
                "reference_folder"
            )
        )


        reference_images = (
            visual_consistency.get(
                "reference_images",
                []
            )
        )


        if not reference_folder:

            return []



        images = []


        for image in reference_images:

            images.append(

                f"{reference_folder}/{image}"

            )


        return images
class CharacterManager:


    def __init__(self, characters_config):

        self.characters = (
            characters_config["characters"]
        )



    def get_character(self, character_id):

        if character_id not in self.characters:

            raise Exception(
                f"Character not found: {character_id}"
            )


        return self.characters[character_id]



    def get_main_character(self, series_id):

        for character_id, character in self.characters.items():

            if character["series"] == series_id:

                if character["importance"] == "Main":

                    return character


        return None
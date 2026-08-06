import json
from pathlib import Path



class CharacterReferenceLoader:


    def __init__(self, character_directory):

        self.directory = Path(
            character_directory
        )

        self.character_file = (
            self.directory / "character.json"
        )



    def load(self):

        with open(
            self.character_file,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)



    def get_reference_images(self):

        character = self.load()


        images = []


        references = (
            character["reference_images"]
        )


        for image in references["images"]:

            image_path = (
                self.directory / image
            )


            if image_path.exists():

                images.append(
                    str(image_path)
                )


        return images



    def build_prompt(self):

        character = self.load()


        visual = (
            character["visual_identity"]
        )


        clothing = visual["clothing"]


        clothing_text = ", ".join(

            [
                f"{item['color']} {item['item']}"

                for item in clothing

            ]

        )


        return f"""

            Character Identity:

            Name:
            {character['name']}


            Species:
            {character['identity']['species']}


            Appearance:

            {visual['body']['fur']}

            {visual['body']['shape']}


            Face:

            {visual['face']['eyes']}


            Clothing:

            {clothing_text}


            Personality:

            {", ".join(character['animation_rules']['personality'])}


            Style:

            3D animated cartoon.
            Family friendly.
            Expressive comedy character.

        """
import json

from pathlib import Path



class CharacterReferenceLoader:


    def __init__(
        self,
        character_directory
    ):

        self.directory = Path(
            character_directory
        )

        self.character_file = (
            self.directory
            /
            "character.json"
        )



    def load(self):

        with open(
            self.character_file,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )



    def get_reference_images(self):

        character = (
            self.load()
        )


        references = (
            character.get(
                "reference_images",
                {}
            )
        )


        images = []


        for image in references.get(
            "images",
            []
        ):


            image_path = (
                self.directory
                /
                image
            )


            if image_path.exists():

                images.append(
                    str(image_path)
                )


        return images



    def get_reference_directory(self):

        return str(
            self.directory
        )



    def build_prompt(self):

        character = (
            self.load()
        )


        visual = (
            character.get(
                "visual_identity",
                {}
            )
        )


        body = (
            visual.get(
                "body",
                {}
            )
        )


        face = (
            visual.get(
                "face",
                {}
            )
        )


        clothing = (
            visual.get(
                "clothing",
                []
            )
        )


        clothing_text = ", ".join(

            [
                f"{item['color']} {item['item']}"

                for item in clothing

            ]

        )


        return (

            f"{character.get('name')} "
            f"the "
            f"{character.get('identity', {}).get('species')}, "
            f"{body.get('size')} "
            f"{body.get('shape')}, "
            f"{body.get('fur')}, "
            f"{face.get('eyes')}, "
            f"wearing {clothing_text}, "
            "3D animated cartoon style, "
            "family friendly."

        )
import requests



class StableDiffusionProvider:


    def __init__(self, config):

        self.url = (
            config["ai_models"]
            ["models"]
            ["image_model"]
            .get(
                "url",
                "http://127.0.0.1:7860"
            )
        )



    def generate(self, prompt):


        response = requests.post(

            f"{self.url}/sdapi/v1/txt2img",

            json={

                "prompt": prompt,

                "steps": 30,

                "width": 1024,

                "height": 1024

            }

        )


        return response.json()
import requests



class OllamaProvider:


    def __init__(self, config):

        self.url = (
            config["ai_models"]
            ["models"]
            ["language_model"]
            .get(
                "url",
                "http://localhost:11434"
            )
        )


        self.model = (
            config["ai_models"]
            ["models"]
            ["language_model"]
            .get(
                "model",
                "llama3"
            )
        )



    def generate(self, prompt):


        response = requests.post(

            f"{self.url}/api/generate",

            json={

                "model": self.model,

                "prompt": prompt,

                "stream": False,

                "format": "json"

            }

        )


        response.raise_for_status()


        return response.json()["response"]
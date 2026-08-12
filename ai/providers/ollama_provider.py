import requests


class OllamaProvider:

    def __init__(
        self,
        config
    ):

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


    def generate(
        self,
        prompt,
        response_format=None
    ):

        request_data = {

            "model": self.model,

            "prompt": prompt,

            "stream": False

        }


        if response_format:

            request_data["format"] = (
                response_format
            )

        else:

            request_data["format"] = "json"


        response = requests.post(

            f"{self.url}/api/generate",

            json=request_data

        )


        response.raise_for_status()


        data = response.json()


        return data["response"]
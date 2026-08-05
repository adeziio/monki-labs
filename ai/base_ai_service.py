class BaseAIService:


    def __init__(self, config):

        self.config = config



    def log(self, message):

        print(
            f"[AI] {message}"
        )
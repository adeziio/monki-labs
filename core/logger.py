from datetime import datetime


class Logger:


    def info(self, message):

        timestamp = datetime.now()

        print(
            f"[{timestamp}] INFO: {message}"
        )



    def error(self, message):

        timestamp = datetime.now()

        print(
            f"[{timestamp}] ERROR: {message}"
        )
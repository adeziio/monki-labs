from pathlib import Path



class FileManager:


    def create_directory(self, path):

        directory = Path(path)

        directory.mkdir(
            parents=True,
            exist_ok=True
        )


    def exists(self, path):

        return Path(path).exists()
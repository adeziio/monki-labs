from pathlib import Path
import json
from datetime import datetime



class EpisodeManager:


    def __init__(self, series_id):

        self.series_id = series_id


        self.base_directory = Path(
            "media/series"
        )


        self.episode_directory = (
            self.create_episode_directory()
        )



    def create_episode_directory(self):


        series_directory = (
            self.base_directory
            /
            self.series_id
        )


        series_directory.mkdir(
            parents=True,
            exist_ok=True
        )


        existing = list(
            series_directory.glob(
                "episode_*"
            )
        )


        episode_number = (
            len(existing) + 1
        )


        episode_directory = (
            series_directory
            /
            f"ep_{episode_number:04}"
        )


        folders = [

            "story",

            "storyboard",

            "scenes",

            "audio",

            "video",

            "thumbnail"

        ]


        for folder in folders:

            (
                episode_directory
                /
                folder
            ).mkdir(
                parents=True,
                exist_ok=True
            )


        return episode_directory



    def get_path(self):

        return self.episode_directory



    def save_json(self, folder, filename, data):


        path = (

            self.episode_directory

            /

            folder

            /

            filename

        )


        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:


            json.dump(

                data,

                file,

                indent=4

            )


        return str(path)
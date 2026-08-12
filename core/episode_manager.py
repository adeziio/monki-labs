from pathlib import Path
import json


class EpisodeManager:

    def __init__(
        self,
        series_id
    ):

        self.series_id = series_id

        self.base_directory = Path(
            "media/series"
        )

        self.series_directory = (
            self.base_directory
            /
            self.series_id
        )

        self.previous_episode_directories = (
            self.get_previous_episode_directories()
        )

        self.episode_directory = (
            self.create_episode_directory()
        )


    def get_previous_episode_directories(
        self
    ):

        if not self.series_directory.exists():

            return []

        episodes = []

        for directory in (
            self.series_directory.glob(
                "ep_*"
            )
        ):

            if not directory.is_dir():

                continue

            episode_number = (
                self.get_episode_number(
                    directory
                )
            )

            if episode_number is None:

                continue

            episodes.append(
                (
                    episode_number,
                    directory
                )
            )

        episodes.sort(
            key=lambda item: item[0]
        )

        return [
            directory
            for _, directory in episodes
        ]


    def get_episode_number(
        self,
        episode_directory
    ):

        try:

            return int(
                episode_directory.name.split(
                    "_"
                )[-1]
            )

        except (
            ValueError,
            IndexError
        ):

            return None


    def get_next_episode_number(
        self
    ):

        episode_numbers = []

        for directory in (
            self.previous_episode_directories
        ):

            episode_number = (
                self.get_episode_number(
                    directory
                )
            )

            if episode_number is not None:

                episode_numbers.append(
                    episode_number
                )

        if not episode_numbers:

            return 1

        return max(
            episode_numbers
        ) + 1


    def create_episode_directory(
        self
    ):

        self.series_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        episode_number = (
            self.get_next_episode_number()
        )

        episode_directory = (
            self.series_directory
            /
            f"ep_{episode_number:04}"
        )

        episode_directory.mkdir(
            parents=True,
            exist_ok=False
        )

        folders = [
            "story",
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


    def get_path(
        self
    ):

        return self.episode_directory


    def load_json(
        self,
        path
    ):

        if not path.exists():

            return None

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            if isinstance(
                data,
                dict
            ):

                return data

        except (
            json.JSONDecodeError,
            OSError
        ):

            pass

        return None


    def get_previous_stories(
        self
    ):

        stories = []

        for episode_directory in (
            self.previous_episode_directories
        ):

            story_path = (
                episode_directory
                /
                "story"
                /
                "story.json"
            )

            story = (
                self.load_json(
                    story_path
                )
            )

            if story is None:

                continue

            stories.append(
                {
                    "episode":
                    self.get_episode_number(
                        episode_directory
                    ),

                    "story":
                    story
                }
            )

        return stories


    def get_previous_story(
        self
    ):

        stories = (
            self.get_previous_stories()
        )

        if not stories:

            return None

        return stories[-1]


    def save_json(
        self,
        folder,
        filename,
        data
    ):

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
                indent=4,
                ensure_ascii=False
            )

        return str(path)
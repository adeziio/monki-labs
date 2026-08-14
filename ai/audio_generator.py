from pathlib import Path
import random

from ai.base_ai_service import BaseAIService


class AudioGenerator(BaseAIService):

    def __init__(
        self,
        config
    ):

        super().__init__(
            config,
            "AUDIO"
        )

        self.audio_rules = (
            config["audio"]
            ["audio_rules"]
        )

        self.active_series = (
            config["series"]
            ["active_series"]
        )

        self.series_config = (
            config["series"]
            ["series"]
            [self.active_series]
        )

        self.music_directory = Path(
            self.audio_rules["music"]["directory"]
        )

    def generate(
        self,
        animations
    ):

        self.log(
            "Generating audio plan"
        )

        music_file = None

        music_rules = (
            self.audio_rules
            .get(
                "music",
                {}
            )
        )

        if music_rules.get(
            "enabled",
            False
        ):

            music_config = (
                self.series_config
                .get(
                    "audio",
                    {}
                )
                .get(
                    "music",
                    {}
                )
            )

            allowed_tracks = (
                music_config.get(
                    "allowed_tracks",
                    []
                )
            )

            available_tracks = []

            for track in allowed_tracks:

                track_path = (
                    self.music_directory
                    /
                    track
                )

                if track_path.exists():

                    available_tracks.append(
                        track_path
                    )

            if available_tracks:

                music_file = str(
                    random.choice(
                        available_tracks
                    )
                )

            else:

                default_track = (
                    music_config.get(
                        "default_track"
                    )
                )

                if default_track:

                    default_path = (
                        self.music_directory
                        /
                        default_track
                    )

                    if default_path.exists():

                        music_file = str(
                            default_path
                        )

            self.log(
                f"Selected music: {music_file}"
            )

        return {
            "music": music_file,

            "sound_effects": [],

            "dialogue": False,

            "voice": False
        }
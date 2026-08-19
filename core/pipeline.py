from core.config_loader import ConfigLoader
from core.logger import Logger
from core.hardware_detector import HardwareDetector

from ai.video_generator import VideoGenerator


class MonkiPipeline:

    def __init__(
        self
    ):

        self.logger = Logger()

        self.hardware = (
            HardwareDetector().detect()
        )

        print(
            f"[SYSTEM] Running on device: "
            f"{self.hardware['device']}"
        )

        loader = ConfigLoader()

        self.config = (
            loader.load_all()
        )

        self.config["hardware"] = (
            self.hardware
        )

        self.video = (
            VideoGenerator(
                self.config
            )
        )

    def set_progress_callback(
        self,
        callback
    ):

        self.video.set_progress_callback(
            callback
        )

    def create_prompt(
        self
    ):

        return (
            self.video.create_prompt()
        )

    def generate_video_from_prompt(
        self,
        prompt_item
    ):

        return (
            self.video.generate_from_prompt(
                prompt_item
            )
        )

    def create_episode(
        self
    ):

        video = (
            self.video.generate()
        )

        return video
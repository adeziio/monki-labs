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

    def create_episode(
        self
    ):

        video = (
            self.video.generate()
        )

        return video
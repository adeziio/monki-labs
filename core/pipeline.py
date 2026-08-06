from core.config_loader import ConfigLoader
from core.logger import Logger
from core.hardware_detector import HardwareDetector

from characters.character_manager import CharacterManager

from ai.story_generator import StoryGenerator
from ai.storyboard_generator import StoryboardGenerator
from ai.image_generator import ImageGenerator
from ai.animation_generator import AnimationGenerator
from ai.audio_generator import AudioGenerator
from ai.thumbnail_generator import ThumbnailGenerator
from ai.video_builder import VideoBuilder
from core.episode_manager import EpisodeManager



class MonkiPipeline:


    def __init__(self):

        self.logger = Logger()


        # Detect hardware first
        self.hardware = HardwareDetector().detect()


        print(
            f"Running on device: {self.hardware['device']}"
        )


        # Load configuration
        loader = ConfigLoader()

        self.config = loader.load_all()



        # Character system
        self.characters = CharacterManager(
            self.config["characters"]
        )


        # AI Services
        self.story = StoryGenerator(
            self.config
        )


        self.storyboard = StoryboardGenerator(
            self.config
        )


        self.images = ImageGenerator(
            self.config
        )


        self.animation = AnimationGenerator(
            self.config
        )


        self.audio = AudioGenerator(
            self.config
        )


        self.thumbnail = ThumbnailGenerator(
            self.config
        )


        self.video = VideoBuilder(
            self.config
        )



    def create_episode(self):

        self.logger.info(
            "Creating new episode"
        )

        episode = EpisodeManager(
            "max_the_monkey"
        )


        episode_path = episode.get_path()


        print(
            f"Episode workspace: {episode_path}"
        )


        story = self.story.generate()


        episode.save_json(
            "story",
            "story.json",
            story
        )


        storyboard = self.storyboard.generate(
            story
        )


        episode.save_json(
            "storyboard",
            "storyboard.json",
            storyboard
        )


        scenes = self.images.generate(
            storyboard,
            episode
        )


        animations = self.animation.generate(
            scenes,
            episode
        )


        audio = self.audio.generate(
            animations
        )


        video = self.video.build(
            animations,
            audio
        )


        thumbnail = self.thumbnail.generate(
            video
        )


        self.logger.info(
            "Episode generation complete"
        )
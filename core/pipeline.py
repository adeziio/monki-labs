from core.config_loader import ConfigLoader
from core.logger import Logger

from characters.character_manager import CharacterManager

from ai.story_generator import StoryGenerator
from ai.storyboard_generator import StoryboardGenerator
from ai.image_generator import ImageGenerator
from ai.animation_generator import AnimationGenerator
from ai.audio_generator import AudioGenerator
from ai.thumbnail_generator import ThumbnailGenerator
from ai.video_builder import VideoBuilder



class MonkiPipeline:


    def __init__(self):


        self.logger = Logger()


        loader = ConfigLoader()


        self.config = loader.load_all()



        self.characters = CharacterManager(
            self.config["characters"]
        )


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


        story = self.story.generate()


        storyboard = self.storyboard.generate(
            story
        )


        scenes = self.images.generate(
            storyboard
        )


        animations = self.animation.generate(
            scenes
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
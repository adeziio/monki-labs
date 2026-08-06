from ai.base_ai_service import BaseAIService

from pathlib import Path

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips
)



class VideoBuilder(BaseAIService):


    def __init__(self, config):

        super().__init__(config)


        self.output_directory = Path(
            "media/output"
        )


        self.output_directory.mkdir(
            parents=True,
            exist_ok=True
        )



    def build(
        self,
        animations,
        audio
    ):


        self.log(
            "Building final video"
        )


        clips = []


        for animation in animations:


            clip = VideoFileClip(
                animation["video"]
            )


            clips.append(
                clip
            )



        if not clips:

            raise Exception(
                "No animation clips found"
            )



        final_video = concatenate_videoclips(
            clips
        )



        music_file = audio.get(
            "music"
        )


        if music_file:


            print(
                f"Adding audio: {music_file}"
            )


            music = AudioFileClip(
                music_file
            )


            if music.duration > final_video.duration:

                music = music.subclipped(
                    0,
                    final_video.duration
                )


            else:

                music = music.with_duration(
                    final_video.duration
                )


            final_video = final_video.with_audio(
                music
            )



        output = (
            self.output_directory
            /
            "episode.mp4"
        )


        final_video.write_videofile(

            str(output),

            fps=24,

            codec="libx264",

            audio_codec="aac",

            temp_audiofile=
            "media/output/temp_audio.m4a",

            remove_temp=True

        )


        for clip in clips:

            clip.close()


        if music_file:

            music.close()


        final_video.close()


        return {

            "output":

            str(output)

        }
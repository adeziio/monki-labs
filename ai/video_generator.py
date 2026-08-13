from pathlib import Path
import random
import re

import torch

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips
)

from diffusers import WanPipeline

from diffusers.utils import export_to_video

from ai.base_ai_service import BaseAIService
from ai.prompt_generator import PromptGenerator


class VideoGenerator(
    BaseAIService
):

    def __init__(
        self,
        config
    ):

        super().__init__(
            config
        )

        self.config = config

        self.hardware = (
            config.get(
                "hardware",
                {}
            )
        )

        self.video_config = (
            config["ai_models"]
            ["models"]
            ["video_model"]
        )

        content_config = (
            config["content"]
        )

        self.active_category = (
            content_config[
                "active_category"
            ]
        )

        self.category_config = (
            content_config[
                "categories"
            ][
                self.active_category
            ]
        )

        self.video_output_config = (
            self.category_config
            .get(
                "video",
                {}
            )
        )

        self.prompt_generator = (
            PromptGenerator(
                config
            )
        )

        self.pipeline = None

        self.output_root = Path(
            "media/output"
        )

        self.category_output_directory = (
            self.output_root
            /
            self.get_category_directory_name()
        )

        self.run_directory = (
            self.create_run_directory()
        )

        self.clip_output_directory = (
            self.run_directory
        )

    def get_category_directory_name(
        self
    ):

        category_name = (
            self.category_config
            .get(
                "name",
                self.active_category
            )
        )

        category_name = str(
            category_name
        ).strip()

        if not category_name:

            category_name = (
                self.active_category
            )

        category_name = re.sub(
            r'[<>:"/\\|?*]',
            "_",
            category_name
        )

        category_name = re.sub(
            r"\s+",
            " ",
            category_name
        )

        return category_name

    def create_run_directory(
        self
    ):

        self.category_output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        existing_numbers = []

        for path in (
            self.category_output_directory.iterdir()
        ):

            if not path.is_dir():

                continue

            if not path.name.isdigit():

                continue

            existing_numbers.append(
                int(
                    path.name
                )
            )

        if existing_numbers:

            next_number = (
                max(
                    existing_numbers
                )
                +
                1
            )

        else:

            next_number = 1

        run_directory = (
            self.category_output_directory
            /
            f"{next_number:03}"
        )

        run_directory.mkdir(
            parents=True,
            exist_ok=False
        )

        self.log(
            f"Output run directory: "
            f"{run_directory}"
        )

        return run_directory

    def get_device(
        self
    ):

        configured_device = (
            self.video_config
            .get(
                "device",
                "cpu"
            )
        )

        if configured_device == "cuda":

            if torch.cuda.is_available():

                return "cuda"

            fallback = (
                self.config
                .get(
                    "ai_models",
                    {}
                )
                .get(
                    "execution",
                    {}
                )
                .get(
                    "fallback",
                    "cpu"
                )
            )

            self.log(
                "CUDA requested but unavailable. "
                f"Using fallback device: {fallback}"
            )

            return fallback

        return configured_device

    def get_dtype(
        self,
        device
    ):

        if device == "cuda":

            return torch.bfloat16

        return torch.float32

    def get_inference_steps(
        self,
        device
    ):

        steps_config = (
            self.video_config
            .get(
                "steps",
                {}
            )
        )

        if not isinstance(
            steps_config,
            dict
        ):

            raise ValueError(
                "Video model steps must be configured "
                "as a device-specific object."
            )

        if device not in steps_config:

            raise ValueError(
                f"No video model steps configured "
                f"for device: {device}"
            )

        steps = int(
            steps_config[
                device
            ]
        )

        if steps <= 0:

            raise ValueError(
                "Video model inference steps "
                "must be greater than zero."
            )

        return steps

    def get_output_resolution(
        self
    ):

        resolution = (
            self.video_output_config
            .get(
                "resolution",
                {}
            )
        )

        width = int(
            resolution.get(
                "width",
                1080
            )
        )

        height = int(
            resolution.get(
                "height",
                1920
            )
        )

        if width <= 0 or height <= 0:

            raise ValueError(
                "Video resolution must contain "
                "positive width and height values."
            )

        return (
            width,
            height
        )

    def get_model_resolution(
        self
    ):

        output_width, output_height = (
            self.get_output_resolution()
        )

        aspect_ratio = (
            output_width
            /
            output_height
        )

        model_max_area = (
            480 * 832
        )

        model_height = (
            int(
                (
                    model_max_area
                    /
                    aspect_ratio
                )
                ** 0.5
            )
        )

        model_width = (
            int(
                model_height
                * aspect_ratio
            )
        )

        model_width = (
            max(
                16,
                (model_width // 16) * 16
            )
        )

        model_height = (
            max(
                16,
                (model_height // 16) * 16
            )
        )

        return (
            model_width,
            model_height
        )

    def get_clip_duration(
        self
    ):

        duration = (
            self.video_output_config
            .get(
                "duration_seconds",
                8
            )
        )

        duration = float(
            duration
        )

        if duration <= 0:

            raise ValueError(
                "Video duration must be greater than zero."
            )

        return duration

    def get_output_fps(
        self
    ):

        fps = (
            self.video_output_config
            .get(
                "fps",
                24
            )
        )

        fps = float(
            fps
        )

        if fps <= 0:

            raise ValueError(
                "Video FPS must be greater than zero."
            )

        return fps

    def get_model_fps(
        self
    ):

        output_fps = (
            self.get_output_fps()
        )

        model_fps = (
            output_fps / 3
        )

        if model_fps <= 0:

            raise ValueError(
                "Derived model FPS must be greater than zero."
            )

        return model_fps

    def get_frame_count(
        self,
        duration
    ):

        model_fps = (
            self.get_model_fps()
        )

        raw_frame_count = (
            duration * model_fps
        )

        frame_count = (
            round(
                (raw_frame_count - 1) / 4
            ) * 4
            + 1
        )

        return max(
            frame_count,
            5
        )

    def load_pipeline(
        self
    ):

        if self.pipeline is not None:

            return

        device = (
            self.get_device()
        )

        dtype = (
            self.get_dtype(
                device
            )
        )

        model_name = (
            self.video_config
            ["model"]
        )

        provider = (
            self.video_config
            .get(
                "provider",
                ""
            )
        )

        if provider.lower() != "wan":

            raise RuntimeError(
                f"Unsupported video provider: {provider}"
            )

        self.log(
            f"Loading video model: {model_name}"
        )

        self.log(
            f"Execution device: {device}"
        )

        self.pipeline = (
            WanPipeline.from_pretrained(
                model_name,
                torch_dtype=dtype
            )
        )

        self.pipeline.to(
            device
        )

    def generate_clip(
        self,
        prompt,
        output_path
    ):

        self.log(
            f"Generating clip: {prompt}"
        )

        device = (
            self.get_device()
        )

        model_width, model_height = (
            self.get_model_resolution()
        )

        steps = (
            self.get_inference_steps(
                device
            )
        )

        guidance_scale = (
            self.video_config
            .get(
                "guidance_scale",
                6.0
            )
        )

        model_fps = (
            self.get_model_fps()
        )

        negative_prompt = (
            self.video_config
            .get(
                "negative_prompt",
                ""
            )
        )

        duration = (
            self.get_clip_duration()
        )

        frames = (
            self.get_frame_count(
                duration
            )
        )

        output_width, output_height = (
            self.get_output_resolution()
        )

        actual_duration = (
            frames / model_fps
        )

        self.log(
            f"Content resolution: "
            f"{output_width}x{output_height}"
        )

        self.log(
            f"Model generation resolution: "
            f"{model_width}x{model_height}"
        )

        self.log(
            f"Target clip duration: "
            f"{duration:.1f} seconds"
        )

        self.log(
            f"Generating {frames} frames "
            f"at {model_fps:g} FPS"
        )

        self.log(
            f"Model clip duration: "
            f"{actual_duration:.3f} seconds"
        )

        self.log(
            f"Inference steps: "
            f"{steps}"
        )

        result = (
            self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                height=model_height,
                width=model_width,
                num_frames=frames,
                guidance_scale=guidance_scale,
                num_inference_steps=steps
            )
        )

        frames_output = (
            result.frames[0]
        )

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        export_to_video(
            frames_output,
            str(output_path),
            fps=model_fps
        )

        return str(
            output_path
        )

    def combine_clips(
        self,
        clip_paths
    ):

        self.log(
            "Combining generated clips"
        )

        clips = []

        for clip_path in clip_paths:

            clips.append(
                VideoFileClip(
                    clip_path
                )
            )

        if not clips:

            raise RuntimeError(
                "No video clips were generated."
            )

        final_video = (
            concatenate_videoclips(
                clips,
                method="compose"
            )
        )

        return (
            final_video,
            clips
        )

    def get_music_path(
        self
    ):

        audio_config = (
            self.config.get(
                "audio",
                {}
            )
        )

        audio_rules = (
            audio_config.get(
                "audio_rules",
                {}
            )
        )

        music_config = (
            audio_rules.get(
                "music",
                {}
            )
        )

        if not music_config.get(
            "enabled",
            False
        ):

            return None

        music_directory = Path(
            music_config.get(
                "directory",
                "assets/audio/music"
            )
        )

        if not music_directory.exists():

            return None

        files = [
            path
            for path in music_directory.iterdir()
            if (
                path.is_file()
                and
                path.suffix.lower()
                in (
                    ".mp3",
                    ".wav",
                    ".m4a",
                    ".ogg"
                )
            )
        ]

        if not files:

            return None

        return str(
            random.choice(
                files
            )
        )

    def add_music(
        self,
        video,
        music_path
    ):

        if not music_path:

            return (
                video,
                None
            )

        music = (
            AudioFileClip(
                music_path
            )
        )

        if music.duration > video.duration:

            music = music.subclipped(
                0,
                video.duration
            )

        else:

            music = music.with_duration(
                video.duration
            )

        video = (
            video.with_audio(
                music
            )
        )

        return (
            video,
            music
        )

    def generate(
        self
    ):

        self.log(
            "Starting short-form video generation"
        )

        generation_config = (
            self.category_config
            .get(
                "generation",
                {}
            )
        )

        clip_count = (
            generation_config
            .get(
                "clip_count",
                1
            )
        )

        prompts = (
            self.prompt_generator
            .generate(
                clip_count
            )
        )

        if not prompts:

            raise RuntimeError(
                "No video prompts were generated."
            )

        self.load_pipeline()

        clip_paths = []

        for index, prompt in enumerate(
            prompts,
            start=1
        ):

            output_path = (
                self.clip_output_directory
                /
                f"clip_{index:03}.mp4"
            )

            clip_path = (
                self.generate_clip(
                    prompt,
                    output_path
                )
            )

            clip_paths.append(
                clip_path
            )

        final_video, clips = (
            self.combine_clips(
                clip_paths
            )
        )

        music_path = (
            self.get_music_path()
        )

        final_video, music = (
            self.add_music(
                final_video,
                music_path
            )
        )

        output_path = (
            self.run_directory
            /
            "episode.mp4"
        )

        output_fps = (
            self.get_output_fps()
        )

        final_video.write_videofile(
            str(output_path),
            fps=output_fps,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=(
                str(
                    self.run_directory
                    / 
                    "temp_audio.m4a"
                )
            ),
            remove_temp=True
        )

        for clip in clips:

            clip.close()

        if music:

            music.close()

        final_video.close()

        self.log(
            f"Final video created: {output_path}"
        )

        return {
            "output": str(
                output_path
            ),
            "clips": clip_paths,
            "prompts": prompts
        }
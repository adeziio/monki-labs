from pathlib import Path
import re

import torch

from moviepy import (
    VideoFileClip,
    concatenate_videoclips
)

from diffusers import LTX2Pipeline

from diffusers.pipelines.ltx2.export_utils import (
    encode_video
)

from diffusers.pipelines.ltx2.utils import (
    DEFAULT_NEGATIVE_PROMPT
)

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
            self.category_config[
                "video"
            ]
        )

        self.audio_config = (
            self.category_config.get(
                "audio",
                {}
            )
        )

        self.generation_config = (
            self.category_config[
                "generation"
            ]
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

        device = (
            self.hardware[
                "device"
            ]
        )

        if device == "auto":

            if torch.cuda.is_available():

                return "cuda"

            return "cpu"

        if device not in (
            "cpu",
            "cuda",
            "mps"
        ):

            raise ValueError(
                "Unsupported execution device: "
                f"{device}"
            )

        if (
            device == "cuda"
            and
            not torch.cuda.is_available()
        ):

            fallback = (
                self.hardware.get(
                    "fallback"
                )
            )

            if fallback:

                self.log(
                    "CUDA requested but unavailable. "
                    f"Using configured fallback: {fallback}"
                )

                return fallback

            raise RuntimeError(
                "CUDA requested but unavailable "
                "and no fallback device is configured."
            )

        return device

    def get_dtype(
        self,
        device
    ):

        dtype_name = (
            self.hardware[
                "torch_dtype"
            ]
        )

        dtype_map = {

            "float32":
            torch.float32,

            "float16":
            torch.float16,

            "bfloat16":
            torch.bfloat16

        }

        if dtype_name not in dtype_map:

            raise ValueError(
                "Unsupported torch dtype: "
                f"{dtype_name}"
            )

        if device == "cpu":

            return torch.float32

        return dtype_map[
            dtype_name
        ]

    def get_generation_resolution(
        self
    ):

        resolution = (
            self.video_config[
                "generation_resolution"
            ]
        )

        width = int(
            resolution[
                "width"
            ]
        )

        height = int(
            resolution[
                "height"
            ]
        )

        if width <= 0 or height <= 0:

            raise ValueError(
                "LTX generation resolution "
                "must contain positive values."
            )

        if width % 32 != 0:

            raise ValueError(
                "LTX generation width must "
                "be divisible by 32."
            )

        if height % 32 != 0:

            raise ValueError(
                "LTX generation height must "
                "be divisible by 32."
            )

        return (
            width,
            height
        )

    def get_generation_fps(
        self
    ):

        fps = float(
            self.video_config[
                "generation_fps"
            ]
        )

        if fps <= 0:

            raise ValueError(
                "LTX generation FPS must "
                "be greater than zero."
            )

        return fps

    def get_output_resolution(
        self
    ):

        resolution = (
            self.video_output_config[
                "resolution"
            ]
        )

        width = int(
            resolution[
                "width"
            ]
        )

        height = int(
            resolution[
                "height"
            ]
        )

        if width <= 0 or height <= 0:

            raise ValueError(
                "Final video resolution must "
                "contain positive values."
            )

        return (
            width,
            height
        )

    def get_output_aspect_ratio(
        self
    ):

        return (
            self.video_output_config[
                "aspect_ratio"
            ]
        )

    def get_output_format(
        self
    ):

        return (
            self.video_output_config[
                "format"
            ]
        )

    def get_clip_duration(
        self
    ):

        duration = float(
            self.video_output_config[
                "duration_seconds"
            ]
        )

        if duration <= 0:

            raise ValueError(
                "Video duration must "
                "be greater than zero."
            )

        return duration

    def get_output_fps(
        self
    ):

        fps = float(
            self.video_output_config[
                "fps"
            ]
        )

        if fps <= 0:

            raise ValueError(
                "Output FPS must "
                "be greater than zero."
            )

        return fps

    def get_frame_count(
        self,
        duration
    ):

        model_fps = (
            self.get_generation_fps()
        )

        raw_frame_count = (
            duration
            *
            model_fps
        )

        frame_count = (
            round(
                (
                    raw_frame_count
                    -
                    1
                )
                /
                8
            )
            *
            8
            +
            1
        )

        return frame_count

    def get_inference_steps(
        self,
        device
    ):

        steps_config = (
            self.video_config[
                "steps"
            ]
        )

        if device not in steps_config:

            raise ValueError(
                "No LTX inference steps "
                f"configured for device: {device}"
            )

        steps = int(
            steps_config[
                device
            ]
        )

        if steps <= 0:

            raise ValueError(
                "LTX inference steps "
                "must be greater than zero."
            )

        return steps

    def get_guidance_scale(
        self
    ):

        guidance_scale = float(
            self.video_config[
                "guidance_scale"
            ]
        )

        if guidance_scale < 0:

            raise ValueError(
                "LTX guidance scale "
                "must not be negative."
            )

        return guidance_scale

    def get_audio_guidance_scale(
        self
    ):

        audio_guidance_scale = float(
            self.video_config[
                "audio_guidance_scale"
            ]
        )

        if audio_guidance_scale < 0:

            raise ValueError(
                "LTX audio guidance scale "
                "must not be negative."
            )

        return audio_guidance_scale

    def get_stg_scale(
        self
    ):

        stg_scale = float(
            self.video_config[
                "stg_scale"
            ]
        )

        if stg_scale < 0:

            raise ValueError(
                "LTX STG scale "
                "must not be negative."
            )

        return stg_scale

    def get_audio_stg_scale(
        self
    ):

        audio_stg_scale = float(
            self.video_config[
                "audio_stg_scale"
            ]
        )

        if audio_stg_scale < 0:

            raise ValueError(
                "LTX audio STG scale "
                "must not be negative."
            )

        return audio_stg_scale

    def get_stg_blocks(
        self
    ):

        if (
            self.get_stg_scale() == 0
            and
            self.get_audio_stg_scale() == 0
        ):

            return None

        blocks_config = (
            self.video_config.get(
                "stg_blocks",
                {}
            )
        )

        blocks = (
            blocks_config.get(
                "indices",
                []
            )
        )

        if not blocks:

            self.log(
                "STG is enabled but no STG block "
                "indices are configured. "
                "STG will not be applied."
            )

            return None

        parsed_blocks = []

        for index in blocks:

            parsed = int(
                index
            )

            if parsed < 0:

                raise ValueError(
                    "STG block indices must "
                    "not be negative: "
                    f"{index}"
                )

            parsed_blocks.append(
                parsed
            )

        return parsed_blocks

    def build_audio_prompt(
        self
    ):

        if not self.audio_config.get(
            "enabled",
            False
        ):

            return ""

        model_audio_config = (
            self.video_config.get(
                "audio",
                {}
            )
        )

        if not model_audio_config.get(
            "enabled",
            True
        ):

            return ""

        music_config = (
            self.audio_config.get(
                "music",
                {}
            )
        )

        if not music_config.get(
            "enabled",
            False
        ):

            return ""

        parts = []

        style = (
            music_config.get(
                "style"
            )
        )

        if style:

            parts.append(
                str(
                    style
                ).strip()
            )

        mood = (
            music_config.get(
                "mood",
                []
            )
        )

        if mood:

            mood_text = ", ".join(
                str(
                    value
                ).strip()
                for value in mood
                if str(
                    value
                ).strip()
            )

            if mood_text:

                parts.append(
                    f"mood: {mood_text}"
                )

        instruments = (
            music_config.get(
                "instruments",
                []
            )
        )

        if instruments:

            instrument_text = ", ".join(
                str(
                    value
                ).strip()
                for value in instruments
                if str(
                    value
                ).strip()
            )

            if instrument_text:

                parts.append(
                    f"instruments: {instrument_text}"
                )

        vocals = (
            music_config.get(
                "vocals"
            )
        )

        if vocals is False:

            parts.append(
                "instrumental only, no vocals"
            )

        if not parts:

            return ""

        return (
            "Background music: "
            +
            "; ".join(
                parts
            )
            +
            "."
        )

    def build_ltx_prompt(
        self,
        prompt
    ):

        audio_prompt = (
            self.build_audio_prompt()
        )

        if not audio_prompt:

            return prompt

        prompt = str(
            prompt
        ).strip()

        if not prompt:

            return audio_prompt

        return (
            prompt
            +
            "\n\n"
            +
            audio_prompt
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
            self.video_config[
                "model"
            ]
        )

        provider = (
            self.video_config[
                "provider"
            ]
        )

        if provider.lower() != "ltx":

            raise RuntimeError(
                "Unsupported video provider: "
                f"{provider}"
            )

        self.log(
            f"Loading video model: "
            f"{model_name}"
        )

        self.log(
            f"Execution device: "
            f"{device}"
        )

        self.log(
            f"Model dtype: "
            f"{dtype}"
        )

        self.pipeline = (
            LTX2Pipeline.from_pretrained(
                model_name,
                torch_dtype=dtype
            )
        )

        if device == "cuda":

            self.configure_cuda_pipeline()

        elif device == "mps":

            self.pipeline.to(
                device
            )

        else:

            self.pipeline.to(
                device
            )

    def configure_cuda_pipeline(
        self
    ):

        allocation_config = (
            self.video_config.get(
                "device_allocation",
                {}
            )
        )

        allocation_mode = (
            allocation_config.get(
                "mode",
                "model"
            )
        )

        if allocation_mode == "gpu":

            self.log(
                "Loading model fully onto GPU. "
                "No CPU offload enabled."
            )

            self.pipeline.to(
                "cuda"
            )

        elif allocation_mode == "sequential":

            self.log(
                "Enabling sequential CPU offload "
                "for minimum VRAM usage. "
                "Note: this is the slowest mode."
            )

            self.pipeline.enable_sequential_cpu_offload()

        elif allocation_mode == "model":

            self.log(
                "Enabling model-level CPU offload "
                "for reduced VRAM usage with "
                "near full-GPU performance."
            )

            self.pipeline.enable_model_cpu_offload()

        else:

            raise ValueError(
                "Unsupported device allocation mode: "
                f"{allocation_mode}. "
                "Expected 'gpu', 'model', or 'sequential'."
            )

        if (
            allocation_config.get(
                "vae_tiling",
                False
            )
            and
            hasattr(
                self.pipeline,
                "enable_vae_tiling"
            )
        ):

            self.log(
                "Enabling VAE tiling "
                "for reduced memory usage."
            )

            self.pipeline.enable_vae_tiling()

        if (
            allocation_config.get(
                "vae_slicing",
                False
            )
            and
            hasattr(
                self.pipeline,
                "enable_vae_slicing"
            )
        ):

            self.log(
                "Enabling VAE slicing "
                "for reduced memory usage."
            )

            self.pipeline.enable_vae_slicing()

        if (
            allocation_config.get(
                "attention_slicing",
                False
            )
            and
            hasattr(
                self.pipeline,
                "enable_attention_slicing"
            )
        ):

            self.log(
                "Enabling attention slicing "
                "for reduced memory usage."
            )

            self.pipeline.enable_attention_slicing()

    def generate_clip(
        self,
        prompt,
        output_path
    ):

        ltx_prompt = (
            self.build_ltx_prompt(
                prompt
            )
        )

        self.log(
            f"Generating audio-video clip: "
            f"{ltx_prompt}"
        )

        device = (
            self.get_device()
        )

        model_width, model_height = (
            self.get_generation_resolution()
        )

        model_fps = (
            self.get_generation_fps()
        )

        steps = (
            self.get_inference_steps(
                device
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

        guidance_scale = (
            self.get_guidance_scale()
        )

        audio_guidance_scale = (
            self.get_audio_guidance_scale()
        )

        stg_scale = (
            self.get_stg_scale()
        )

        audio_stg_scale = (
            self.get_audio_stg_scale()
        )

        stg_blocks = (
            self.get_stg_blocks()
        )

        audio_modality_scale = float(
            self.video_config[
                "audio_modality_scale"
            ]
        )

        negative_prompt = (
            self.video_config.get(
                "negative_prompt",
                DEFAULT_NEGATIVE_PROMPT
            )
        )

        output_width, output_height = (
            self.get_output_resolution()
        )

        output_fps = (
            self.get_output_fps()
        )

        actual_duration = (
            frames
            /
            model_fps
        )

        self.log(
            f"Final content resolution: "
            f"{output_width}x{output_height}"
        )

        self.log(
            f"Final aspect ratio: "
            f"{self.get_output_aspect_ratio()}"
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
            f"Model generation FPS: "
            f"{model_fps:g}"
        )

        self.log(
            f"Final output FPS: "
            f"{output_fps:g}"
        )

        self.log(
            f"Generating {frames} frames"
        )

        self.log(
            f"Model clip duration: "
            f"{actual_duration:.3f} seconds"
        )

        self.log(
            f"Inference steps: "
            f"{steps}"
        )

        self.log(
            f"Guidance scale: "
            f"{guidance_scale:g}"
        )

        self.log(
            f"Audio guidance scale: "
            f"{audio_guidance_scale:g}"
        )

        self.log(
            f"STG scale: "
            f"{stg_scale:g}"
        )

        self.log(
            f"Audio STG scale: "
            f"{audio_stg_scale:g}"
        )

        if (
            stg_scale == 0
            and
            audio_stg_scale == 0
        ):

            self.log(
                "Spatio-Temporal Guidance: disabled"
            )

        else:

            self.log(
                "Spatio-Temporal Guidance: enabled"
            )

        if stg_blocks:

            self.log(
                "STG applied to blocks: "
                f"{stg_blocks}"
            )

        else:

            self.log(
                "STG block indices: not applied"
            )

        if self.build_audio_prompt():

            self.log(
                "LTX background music: enabled"
            )

        else:

            self.log(
                "LTX background music: disabled"
            )

        video, audio = (
            self.pipeline(
                prompt=ltx_prompt,
                negative_prompt=negative_prompt,
                width=model_width,
                height=model_height,
                num_frames=frames,
                frame_rate=model_fps,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                audio_guidance_scale=audio_guidance_scale,
                audio_stg_scale=audio_stg_scale,
                stg_scale=stg_scale,
                audio_modality_scale=audio_modality_scale,
                spatio_temporal_guidance_blocks=stg_blocks,
                output_type="np",
                return_dict=False
            )
        )

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        encode_video(
            video[0],
            fps=model_fps,
            audio=audio[0]
            .float()
            .cpu(),
            audio_sample_rate=(
                self.pipeline
                .vocoder
                .config
                .output_sampling_rate
            ),
            output_path=str(
                output_path
            )
        )

        return str(
            output_path
        )

    def combine_clips(
        self,
        clip_paths
    ):

        self.log(
            "Combining generated audio-video clips"
        )

        clips = []

        try:

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

        except Exception:

            for clip in clips:

                clip.close()

            raise

    def write_prompt_file(
        self,
        prompts
    ):

        prompt_path = (
            self.run_directory
            /
            "prompt.txt"
        )

        sections = []

        for index, item in enumerate(
            prompts,
            start=1
        ):

            title = (
                str(
                    item.get(
                        "title",
                        ""
                    )
                ).strip()
            )

            prompt = (
                str(
                    item.get(
                        "prompt",
                        ""
                    )
                ).strip()
            )

            if not title or not prompt:

                continue

            sections.append(
                "\n".join(
                    [
                        f"TITLE: {title}",
                        f"PROMPT: {prompt}"
                    ]
                )
            )

        if not sections:

            raise RuntimeError(
                "No usable prompts available "
                "for prompt.txt."
            )

        prompt_path.write_text(
            "\n\n"
            +
            (
                "\n\n"
                +
                ("=" * 72)
                +
                "\n\n"
            ).join(
                sections
            )
            +
            "\n",
            encoding="utf-8"
        )

        self.log(
            f"Prompt file created: "
            f"{prompt_path}"
        )

        return str(
            prompt_path
        )

    def cleanup_intermediate_clips(
        self,
        clip_paths
    ):

        for clip_path in clip_paths:

            path = Path(
                clip_path
            )

            if not path.exists():

                continue

            try:

                path.unlink()

                self.log(
                    f"Removed intermediate clip: "
                    f"{path.name}"
                )

            except OSError as error:

                self.log(
                    f"Could not remove intermediate "
                    f"clip {path.name}: {error}"
                )

    def generate(
        self
    ):

        self.log(
            "Starting short-form "
            "audio-video generation"
        )

        clip_count = int(
            self.generation_config[
                "clip_count"
            ]
        )

        if clip_count <= 0:

            raise ValueError(
                "Generation clip count "
                "must be greater than zero."
            )

        prompts = (
            self.prompt_generator
            .generate(
                clip_count
            )
        )

        if not prompts:

            raise RuntimeError(
                "No video prompts "
                "were generated."
            )

        if len(prompts) != clip_count:

            self.log(
                f"Requested {clip_count} prompts "
                f"but received {len(prompts)} usable prompts."
            )

        self.write_prompt_file(
            prompts
        )

        self.load_pipeline()

        clip_paths = []

        try:

            for index, item in enumerate(
                prompts,
                start=1
            ):

                prompt = (
                    str(
                        item.get(
                            "prompt",
                            ""
                        )
                    ).strip()
                )

                if not prompt:

                    continue

                output_path = (
                    self.clip_output_directory
                    /
                    f"_clip_{index:03}.mp4"
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

            if not clip_paths:

                raise RuntimeError(
                    "No video clips were generated."
                )

            final_video, clips = (
                self.combine_clips(
                    clip_paths
                )
            )

            try:

                output_format = (
                    self.get_output_format()
                )

                if output_format.lower() != "mp4":

                    raise ValueError(
                        "The current LTX video "
                        "export pipeline requires "
                        "MP4 output."
                    )

                output_path = (
                    self.run_directory
                    /
                    f"episode.{output_format}"
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
                            "_temp_audio.m4a"
                        )
                    ),
                    remove_temp=True
                )

            finally:

                for clip in clips:

                    clip.close()

                final_video.close()

            self.cleanup_intermediate_clips(
                clip_paths
            )

            self.log(
                f"Final audio-video created: "
                f"{output_path}"
            )

            return {
                "output": str(
                    output_path
                ),
                "prompt_file": str(
                    self.run_directory
                    /
                    "prompt.txt"
                ),
                "prompts": prompts
            }

        except Exception:

            self.cleanup_intermediate_clips(
                clip_paths
            )

            raise
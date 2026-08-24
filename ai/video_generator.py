from pathlib import Path
import re
import time

import torch

from moviepy import (
    VideoFileClip,
    concatenate_videoclips
)

from diffusers import LTX2Pipeline

try:
    from diffusers.utils import (
        encode_video
    )
except ImportError:
    from diffusers.pipelines.ltx2.export_utils import (
        encode_video
    )

from diffusers.pipelines.ltx2.utils import (
    DEFAULT_NEGATIVE_PROMPT
)

from ai.base_ai_service import BaseAIService
from ai.memory_utils import (
    get_cuda_memory_summary,
    is_memory_error,
    release_memory
)
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

        self.progress_callback = None

        self.output_root = Path(
            "media/output"
        )

        self.category_output_directory = (
            self.output_root
            /
            self.get_category_directory_name()
        )

        self.run_directory = None

        self.clip_output_directory = None

    def set_progress_callback(
        self,
        callback
    ):

        self.progress_callback = callback

    def get_generation_retry_settings(self):

        attempts = int(
            self.video_config.get(
                "generation_retry_attempts",
                2
            )
        )

        backoff_seconds = float(
            self.video_config.get(
                "generation_retry_backoff_seconds",
                20
            )
        )

        attempts = max(
            0,
            attempts
        )

        backoff_seconds = max(
            0.0,
            backoff_seconds
        )

        return attempts, backoff_seconds

    def release_pipeline_memory(
        self,
        aggressive=False
    ):

        """
        Drops the video model and releases RAM/VRAM so the next
        generation starts from a clean slate. Safe to call when the
        model is already released.
        """

        if self.pipeline is not None:

            summary = get_cuda_memory_summary()

            self.log(
                "Releasing video model from memory."
                + (
                    f" ({summary})"
                    if summary
                    else ""
                )
            )

            self.pipeline = None

        release_memory(
            aggressive=aggressive
        )

    def run_with_generation_retries(
        self,
        description,
        operation,
        stage="video"
    ):

        """
        Runs a video-generation operation and automatically retries
        when any exception occurs. Memory-related failures trigger an
        aggressive VRAM/RAM cleanup before the retry.
        """

        max_retries, backoff_seconds = (
            self.get_generation_retry_settings()
        )

        attempt = 0

        while True:

            try:

                return operation()

            except Exception as error:

                if attempt >= max_retries:

                    self.log(
                        f"{description} failed after "
                        f"{attempt + 1} attempt(s): {error}"
                    )

                    raise

                attempt += 1

                memory_error = is_memory_error(error)

                error_kind = (
                    "memory"
                    if memory_error
                    else "unexpected"
                )

                wait_seconds = (
                    backoff_seconds
                    *
                    attempt
                )

                self.log(
                    f"{description} failed with an {error_kind} "
                    f"error on attempt {attempt} "
                    f"(of {max_retries + 1}): {error}"
                )

                self.release_pipeline_memory(
                    aggressive=memory_error
                )

                self.update_progress(
                    14,
                    f"{description} failed. Cleaning up memory "
                    f"and retrying (attempt {attempt})...",
                    stage=stage
                )

                if wait_seconds > 0:

                    self.log(
                        f"Waiting {wait_seconds:g} seconds "
                        f"before retry {attempt}."
                    )

                    time.sleep(wait_seconds)

    def update_progress(
        self,
        percent,
        message="",
        stage=None
    ):

        percent = max(
            0,
            min(
                100,
                int(percent)
            )
        )

        if self.progress_callback is not None:

            try:

                self.progress_callback(
                    percent,
                    str(message),
                    stage
                )

            except TypeError:

                try:

                    self.progress_callback(
                        percent,
                        str(message)
                    )

                except Exception:

                    pass

            except Exception:

                pass

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

    def start_new_run(
        self
    ):

        self.run_directory = (
            self.create_run_directory()
        )

        self.clip_output_directory = (
            self.run_directory
        )

        return self.run_directory

    def use_existing_run(
        self,
        episode_id
    ):

        if not episode_id:

            raise ValueError(
                "Episode ID is required."
            )

        episode_path = (
            Path(
                episode_id
            )
            .resolve()
        )

        category_path = (
            self.category_output_directory
            .resolve()
        )

        media_root = (
            self.output_root
            .resolve()
        )

        if (
            media_root
            not in episode_path.parents
        ):

            raise ValueError(
                "Invalid episode path."
            )

        if (
            episode_path.parent
            !=
            category_path
        ):

            raise ValueError(
                "Episode does not belong to "
                "the active category."
            )

        if not episode_path.is_dir():

            raise ValueError(
                "Episode directory does not exist: "
                f"{episode_path}"
            )

        if not episode_path.name.isdigit():

            raise ValueError(
                "Invalid episode directory."
            )

        prompt_path = (
            episode_path
            /
            "prompt.txt"
        )

        if not prompt_path.is_file():

            raise ValueError(
                "Episode does not contain "
                "a prompt.txt file."
            )

        self.run_directory = (
            episode_path
        )

        self.clip_output_directory = (
            episode_path
        )

        self.log(
            f"Using existing episode directory: "
            f"{episode_path}"
        )

        return episode_path

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

    def get_modality_scale(
        self
    ):

        modality_scale = float(
            self.video_config[
                "modality_scale"
            ]
        )

        if modality_scale < 0:

            raise ValueError(
                "LTX modality scale "
                "must not be negative."
            )

        return modality_scale

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

    def load_pipeline(
        self
    ):

        if self.pipeline is not None:

            return

        self.update_progress(
            5,
            "Loading video model...",
            stage="video"
        )

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

        # Free any leftover RAM/VRAM from previous runs so the
        # ~50GB model load starts from the cleanest state possible.

        release_memory()

        # Newer diffusers versions renamed `torch_dtype` to `dtype`.
        # Try the new argument first and fall back for older installs.

        try:

            self.pipeline = (
                LTX2Pipeline.from_pretrained(
                    model_name,
                    dtype=dtype,
                    low_cpu_mem_usage=True
                )
            )

        except TypeError:

            self.log(
                "diffusers rejected `dtype`; "
                "falling back to `torch_dtype`."
            )

            self.pipeline = (
                LTX2Pipeline.from_pretrained(
                    model_name,
                    torch_dtype=dtype,
                    low_cpu_mem_usage=True
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

        # Release loader temporaries and defragment CUDA memory
        # after the model is resident on its target device.

        release_memory()

        self.update_progress(
            12,
            "Video model loaded.",
            stage="video"
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

            target_dtype = (
                self.get_dtype(
                    "cuda"
                )
            )

            self.pipeline.to(
                device="cuda",
                dtype=target_dtype
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

    def create_prompt(
        self
    ):

        self.update_progress(
            5,
            "Generating prompt...",
            stage="prompt"
        )

        prompts = (
            self.prompt_generator.generate(
                1
            )
        )

        if not prompts:

            raise RuntimeError(
                "No video prompt was generated."
            )

        prompt_item = prompts[0]

        self.start_new_run()

        self.write_prompt_file(
            [prompt_item]
        )

        self.update_progress(
            100,
            "Prompt created.",
            stage="prompt"
        )

        return {
            "run_directory": str(
                self.run_directory
            ),
            "prompt_file": str(
                self.run_directory
                /
                "prompt.txt"
            ),
            "title": prompt_item[
                "title"
            ],
            "prompt": prompt_item[
                "prompt"
            ]
        }

    def generate_clip(
        self,
        prompt,
        output_path
    ):

        ltx_prompt = (
            str(
                prompt
            ).strip()
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

        modality_scale = (
            self.get_modality_scale()
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
            f"Modality guidance scale: "
            f"{modality_scale:g}"
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

        if self.audio_config.get(
            "enabled",
            False
        ):

            self.log(
                "LTX integrated audio: enabled "
                "(music and SFX derived from prompt)"
            )

        else:

            self.log(
                "LTX integrated audio: disabled"
            )

        self.update_progress(
            15,
            "Starting video generation...",
            stage="video"
        )

        def generation_callback(
            pipeline,
            step,
            timestep,
            callback_kwargs
        ):

            progress = (
                15
                +
                (
                    (
                        step
                        +
                        1
                    )
                    /
                    max(
                        steps,
                        1
                    )
                )
                *
                70
            )

            self.update_progress(
                progress,
                f"Generating video... "
                f"{step + 1}/{steps}",
                stage="video"
            )

            return callback_kwargs

        def execute_generation():

            if self.pipeline is None:

                self.log(
                    "Video model was released. "
                    "Reloading before retry."
                )

                self.load_pipeline()

            return self.pipeline(
                prompt=ltx_prompt,
                negative_prompt=negative_prompt,
                width=model_width,
                height=model_height,
                num_frames=frames,
                frame_rate=model_fps,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                modality_scale=modality_scale,
                audio_guidance_scale=audio_guidance_scale,
                audio_stg_scale=audio_stg_scale,
                stg_scale=stg_scale,
                audio_modality_scale=audio_modality_scale,
                spatio_temporal_guidance_blocks=stg_blocks,
                callback_on_step_end=generation_callback,
                output_type="np",
                return_dict=False
            )

        video, audio = (
            self.run_with_generation_retries(
                "Clip generation",
                execute_generation
            )
        )

        self.update_progress(
            88,
            "Encoding video...",
            stage="video"
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

        del video
        del audio

        release_memory()

        self.update_progress(
            92,
            "Video encoded.",
            stage="video"
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

        if self.run_directory is None:

            raise RuntimeError(
                "No active run directory."
            )

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
            "\n"
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

    def generate_from_prompt(
        self,
        prompt_item,
        episode_id
    ):

        if not isinstance(
            prompt_item,
            dict
        ):

            raise ValueError(
                "Prompt item must be a dictionary."
            )

        title = str(
            prompt_item.get(
                "title",
                ""
            )
        ).strip()

        prompt = str(
            prompt_item.get(
                "prompt",
                ""
            )
        ).strip()

        if not prompt:

            raise ValueError(
                "Selected prompt is empty."
            )

        self.update_progress(
            1,
            "Preparing video generation...",
            stage="video"
        )

        self.use_existing_run(
            episode_id
        )

        self.log(
            f"Generating video for existing "
            f"episode: {self.run_directory}"
        )

        self.load_pipeline()

        clip_paths = []

        try:

            output_path = (
                self.clip_output_directory
                /
                "_clip_001.mp4"
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

            self.update_progress(
                93,
                "Releasing video model...",
                stage="video"
            )

            self.release_pipeline_memory()

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

                self.update_progress(
                    95,
                    "Finalizing episode...",
                    stage="video"
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
                    remove_temp=True,
                    logger=None
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

            self.update_progress(
                100,
                "Video generation complete.",
                stage="video"
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
                "title": title,
                "prompt": prompt
            }

        except Exception:

            self.cleanup_intermediate_clips(
                clip_paths
            )

            raise

        finally:

            self.release_pipeline_memory()

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

        self.update_progress(
            1,
            "Generating prompts...",
            stage="prompt"
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

        self.start_new_run()

        self.write_prompt_file(
            prompts
        )

        self.update_progress(
            100,
            "Prompt file created.",
            stage="prompt"
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

                release_memory()

            self.log(
                "All clips generated. "
                "Releasing video model from memory "
                "before final assembly."
            )

            self.release_pipeline_memory()

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

                self.update_progress(
                    95,
                    "Finalizing episode...",
                    stage="video"
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

            self.update_progress(
                100,
                "Episode generation complete.",
                stage="video"
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

        finally:

            self.release_pipeline_memory()

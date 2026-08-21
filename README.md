# 🐒 Monki Labs

Monki Labs is an AI video generation studio for creating short-form vertical videos with minimal human interaction.

The project supports local and cloud GPU execution, with a web UI for generation, episode management, replay automation, and YouTube uploads.

---

## 🎯 Goals

Monki Labs aims to:

* 🤖 Automatically generate video concepts using a local language model

* 🎬 Generate short-form AI videos from those concepts

* 🎵 Generate video, background music, and sound effects together

* 📱 Produce vertical 9:16 videos optimized for short-form platforms

* 📦 Organize generated content automatically by category and run

* ☁️ Support GPU-based cloud execution

* 🔄 Eventually run automatically without requiring a local PC

* 📅 Support recurring automated video generation and publishing

* 💰 Remain completely free to operate using local/open-source models and free infrastructure where possible

The long-term vision is a pipeline that can run independently, generate quality content, and eventually publish videos automatically.

---

## 🧠 Current Pipeline

At a high level:

```text
Content Configuration

        ↓

Local LLM

        ↓

AI Video Prompt

        ↓

LTX-2.3 Video Generation

        ↓

Video + Background Music + Sound Effects

        ↓

Final MP4

        ↓

Organized Output
```

The application is **configuration-driven**, allowing content and AI settings to be changed without modifying the core pipeline.

The video generation architecture supports both:

* **Single-prompt generation** for one continuous video

* **Multiple-prompt generation** for multiple coherent clips that are combined into one final video

This allows the number of generated clips to be changed through configuration without redesigning the pipeline.

---

## 🛠️ Tech Stack

### AI

* 🧠 Ollama

* 🤖 Qwen 3 8B

* 🎥 LTX-2.3

* 🤗 Hugging Face Diffusers

* 🔥 PyTorch

### Video

* 🎬 MoviePy

* FFmpeg

* ImageIO

### Application

* 🐍 Python 3.12

* JSON configuration

* Virtual environments

### Development

* VS Code

* Git / GitHub

* Pytest

* Black

* Flake8

---

## 📁 Project Structure

```text
monki-labs/

│

├── ai/

│   ├── __init__.py

│   ├── base_ai_service.py

│   ├── prompt_generator.py

│   ├── video_generator.py

│   └── providers/

│       ├── __init__.py

│       └── ollama_provider.py

│

├── config/

│   ├── ai_models.json

│   ├── content.json

│   ├── youtube.json

│

├── core/

│   ├── __init__.py

│   ├── config_loader.py

│   ├── hardware_detector.py

│   └── pipeline.py

│

├── web/

│   ├── index.html

│   ├── job_worker.py

│   └── server.py

│

├── youtube/

│   ├── __init__.py

│   ├── auth.py

│   ├── config.py

│   ├── metadata_generator.py

│   ├── oauth_helper.py

│   ├── channel.py

│   └── uploader.py

│

├── media/

│   └── output/

│

├── .gitignore

├── install_linux.sh

├── install_windows.bat

├── main.py

├── README.md

├── requirements.txt

├── run_linux.sh

├── run_windows.bat

└── .venv/ (created locally after install)
```

The active runtime interface is split between the CLI pipeline and the web UI. The web server and job worker live in `web/server.py` and `web/job_worker.py`, while the AI generation logic remains in the `ai/` and `core/` packages.

---

# 💻 Local Setup

Monki Labs is developed locally on Windows using Python 3.12, but the same repo also supports Linux/GPU execution.

## 1. Clone the repository

```powershell
git clone https://github.com/YOUR_USERNAME/monki-labs.git

cd monki-labs
```

If the repository is private, authenticate with GitHub when prompted.

---

## 2. Install dependencies

Run the Windows installer:

```powershell
.\install_windows.bat
```

The installer:

* Checks for Python

* Creates the `.venv` virtual environment

* Detects whether an NVIDIA GPU is available

* Installs the appropriate PyTorch build

* Installs project dependencies

* Checks for FFmpeg

* Verifies PyTorch and CUDA availability

---

## 3. Run Monki Labs

Run the pipeline from the CLI:

```powershell
.\.venv\Scripts\activate

python main.py
```

Run the browser-based UI locally (quick start):

* On Windows (recommended for local development):

```powershell
.\run_windows.bat
```

* On Linux / RunPod (example):

```bash
bash run_linux.sh
```

Both of those scripts start the same web UI and backend pipeline. Alternatively you can start the HTTP server directly:

```powershell
python web/server.py
```

Then open the UI in a browser:

```text
http://localhost:8000
```

UI: Quick guide

* Start the UI using one of the commands above. The server listens on port 8000 by default.

* The UI lets you:

  * Browse generated episodes (media/output/)

  * Start a new generation job (full episode or single prompt)

  * Monitor per-stage progress (prompt generation and video generation)

  * See job status and any error messages returned by the pipeline

![UI overview](web/screenshots/overview.png)

---

## 4. Development Workflow

The normal development workflow is:

```text
Edit code

   ↓

.\run_windows.bat

   ↓

Review generated video

   ↓

Make changes

   ↓

.\run_windows.bat
```

Generated videos are stored under:

```text
media/output/
```

Output runs are automatically organized by content category and run number.

For example:

```text
media/

└── output/

    └── brainrot/

        ├── 001/

        │   ├── episode.mp4

        │   └── prompt.txt

        ├── 002/

        │   ├── episode.mp4

        │   └── prompt.txt

        └── 003/

            ├── episode.mp4

            └── prompt.txt
```

Each run retains only the **final video** and the **prompt used to generate it**.

Intermediate generated clips are not retained.

---

# ☁️ RunPod / Linux Setup

Monki Labs can run on Linux-based GPU environments such as RunPod without changing the application code.

The same repository and `main.py` are used locally and on cloud GPU environments.

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/monki-labs.git

cd monki-labs
```

For a private repository, authenticate with GitHub and clone the repository.

---

## 2. Install dependencies

Run the Linux installer:

```bash
bash install_linux.sh
```

The installer:

* Creates the Python virtual environment

* Checks for FFmpeg

* Checks for the available GPU environment

* Installs project dependencies

* Verifies PyTorch and CUDA availability

---

## 3. Run Monki Labs

```bash
bash run_linux.sh
```

The Linux runner:

* Starts Ollama with GPU acceleration (fast prompt generation)

* Configures PyTorch CUDA memory handling (`expandable_segments:True`)

* Runs the main pipeline

No application code changes are required to run the pipeline on Linux.

---

## 4. Access the Web UI from Your Browser

When running Monki Labs on a RunPod instance, the web UI runs inside the pod on port `8000`.

RunPod must expose port `8000` as an **HTTP port** so the UI can be accessed from a normal browser outside the pod.

### RunPod port configuration

In the RunPod pod configuration, find:

```text
Expose HTTP ports
```

Add:

```text
8000
```

The exact available ports and services depend on the RunPod pod configuration and template.

For Monki Labs, the important requirement is:

```text
HTTP:
    8000 → Monki Labs
```

If Jupyter is also available through the pod, it may use port `8888`. However, some RunPod configurations or templates may only allow one exposed HTTP service at a time. **Jupyter is not required to run Monki Labs.**

The RunPod Web Terminal can be used instead for command-line access to the pod.

### RunPod Web Terminal

RunPod may provide a browser-accessible Web Terminal on a port such as:

```text
19123
```

This terminal can be used to:

* Run Linux commands

* Activate the Python virtual environment

* Start and stop Monki Labs

* Inspect files and logs

* Manage the running application

The Web Terminal is separate from the Monki Labs HTTP service.

A typical setup can therefore be:

```text
HTTP
└── 8000 → Monki Labs

TCP
└── 22 → SSH

RunPod Web Terminal
└── 19123 → Terminal
```

The exact Web Terminal port is provided by RunPod and may vary.

### Start the Monki Labs server

The web server listens on port `8000` by default.

For example:

```bash
python web/server.py
```

or use the normal RunPod/Linux runner:

```bash
bash run_linux.sh
```

The server must listen on port `8000` so that RunPod can forward browser requests to the application.

### Open the UI

After port `8000` has been exposed, RunPod provides an HTTP proxy URL similar to:

```text
https://<pod-id>-8000.proxy.runpod.net
```

Open that URL in your normal browser.

The exact URL is generated by RunPod and will vary by pod.

### Important

`localhost:8000` refers to the RunPod machine itself. It is **not** the URL to use from your local computer.

When accessing Monki Labs from your own browser, use the RunPod HTTP proxy URL for port `8000`.

For example:

```text
https://<pod-id>-8000.proxy.runpod.net
```

This allows the Monki Labs web UI to be accessed remotely while the application and LTX-2.3 generation process run on the RunPod GPU.

---

## 5. Temporary GPU Environments

RunPod instances can be treated as temporary compute environments.

The repository contains the application and configuration, while generated videos can be retrieved before terminating the instance.

The long-term goal is to use temporary GPU infrastructure only when video generation is required rather than maintaining a continuously running server.

---

# 🖥️ Hardware Requirements

LTX-2.3 is a large model (~50GB in bfloat16). It requires substantial GPU and system memory.

## Minimum (production)

| Component      | Requirement                         |
| -------------- | ----------------------------------- |
| **GPU VRAM**   | 48GB (RTX A6000, RTX L40S)          |
| **System RAM** | 100GB+                              |
| **Storage**    | 200GB+ NVMe (model cache + outputs) |
| **CPU**        | 8+ cores                            |

## Recommended (production)

| Component      | Recommendation        |
| -------------- | --------------------- |
| **GPU**        | RTX L40S (48GB VRAM)  |
| **System RAM** | 100GB+                |
| **Cost**       | ~$1.00/hour on RunPod |

## Why 48GB VRAM is required

The LTX-2.3 pipeline includes a Gemma 3 text encoder (~16GB) plus a video transformer, VAE, and audio components. The full model is ~50GB in bfloat16 — it cannot fit entirely on a 24GB GPU. The pipeline uses **model-level CPU offload** (`enable_model_cpu_offload`) to keep only the active component on GPU at a time, which requires 48GB VRAM.

## Local development

No consumer laptop GPU (8-16GB VRAM) can run this model. For local development, use a **dry-run / test mode** that validates pipeline logic on CPU without loading the full model. Production generation should use cloud GPU instances.

---

# 🏭 Production Configuration

The following configuration has been tested and verified to run end-to-end on an RTX L40S (48GB VRAM, 100GB+ RAM):

## `config/ai_models.json` (video model)

```json
{
    "device_allocation": {
        "mode": "model",
        "vae_tiling": false,
        "vae_slicing": true,
        "attention_slicing": false
    },
    "generation_resolution": {
        "width": 768,
        "height": 1344
    },
    "steps": { "cpu": 8, "cuda": 25 },
    "stg_scale": 1.5,
    "audio_stg_scale": 0.0,
    "guidance_scale": 3.5,
    "audio_guidance_scale": 5.0,
    "stg_blocks": { "indices": [28] }
}
```

## `config/content.json` (content)

```json
{
    "video": {
        "duration_seconds": 6,
        "aspect_ratio": "9:16",
        "fps": 30,
        "resolution": { "width": 1080, "height": 1920 }
    },
    "generation": {
        "clip_count": 2
    }
}
```

## Key settings explained

* **`mode: "model"`** — model-level CPU offload. Keeps only the active component on GPU. Required for 48GB VRAM.

* **`generation_resolution: 768×1344`** — the generation resolution. Output is upscaled to 1080×1920. Higher resolutions (e.g., 896×1600) are possible but increase VRAM usage.

* **`clip_count: 2` × `duration_seconds: 6`** — two 6-second clips concatenated into a 12-second episode. This multi-clip architecture is required because the transformer must hold all frames' latents in VRAM simultaneously — a single 12s clip (289 frames) exceeds 48GB.

* **`stg_scale: 1.5`** — Spatio-Temporal Guidance applied to block 28. Improves sharpness and motion coherence.

* **`audio_stg_scale: 0.0`** — audio STG disabled to reduce VRAM. Audio (music + SFX) is still generated.

* **`low_cpu_mem_usage: true`** — loads the model directly in bfloat16, avoiding the fp32 double-buffer peak during load.

## Expected performance (L40S)

| Metric                          | Value                   |
| ------------------------------- | ----------------------- |
| Per clip (25 steps, 145 frames) | ~9-10 min               |
| Full episode (2 clips + encode) | ~20-25 min              |
| Cost @ ~$1.00/hr                | ~$0.35-0.45 per episode |

---

# ⚙️ Configuration

Monki Labs is **configuration-driven**.

Core behavior is controlled through JSON configuration files rather than hard-coded application logic.

This allows the pipeline to evolve without repeatedly modifying Python code.

Configuration covers areas such as:

* Content categories

* Video duration and output requirements

* Video generation resolution

* Video generation FPS

* Inference steps

* Guidance settings

* AI model selection

* Audio generation behavior

* YouTube configuration

* Studio-level settings

The application reads the appropriate configuration at runtime.

---

# 🎥 Video Generation

Monki Labs currently uses **LTX-2.3** for AI video generation.

The video model generates the visual content and associated audio in the same generation process.

Content configuration controls the final video requirements, including:

* Duration

* Aspect ratio

* Output FPS

* Resolution

* Video format

AI model configuration separately controls generation-specific settings such as:

* Generation resolution

* Generation FPS

* Inference steps

* Guidance scale

* Audio guidance

* Spatio-temporal guidance

* Negative prompts

This keeps output requirements and model-specific generation settings configurable without hard-coding them into the application.

---

# 📝 Prompt Generation

Video concepts are generated using a local Ollama language model.

The prompt generator creates visual concepts designed specifically for AI video generation.

Prompts prioritize:

* Clear physical movement

* Movement through the environment

* Environmental interaction

* Camera movement

* Visual comedy

* Escalation

* Strong visual payoff

* Clear and concise visual descriptions

The system does not rely on preconfigured characters or character references.

The video model is free to generate the visual subjects based entirely on the generated prompt.

---

# 🎞️ Prompt and Episode Generation

# 📺 YouTube Uploads

Completed episodes can be uploaded directly from the web UI. Each episode card with a finished `episode.mp4` includes an **Upload to YouTube** button that opens a metadata and authentication modal.

![YouTube upload modal](web/screenshots/youtube.png)


### Upload metadata

The modal allows the following video fields to be reviewed and changed before upload:

* **Channel Name** — human-readable channel name. The server resolves this through the authenticated Google account using `channels.list(mine=true)` and refuses missing, unmatched, or ambiguous names.

* **Title** — prefilled from the `TITLE:` value in the episode's `prompt.txt`.

* **Description** — prefilled from the episode title and `PROMPT:` text.

* **Tags** — comma-separated YouTube tags.

* **Category ID** — YouTube's numeric category identifier. The default is `24` (Entertainment).

* **Privacy Status** — `private`, `unlisted`, or `public`.

* **Made for Kids** — controls the corresponding YouTube audience declaration.

### OAuth credentials

The account section contains only the values needed for OAuth authentication:

* OAuth Client ID
* OAuth Client Secret
* Refresh Token

Credentials are loaded from `.env` using these keys:

```env
youtube_client_id=YOUR_CLIENT_ID
youtube_client_secret=YOUR_CLIENT_SECRET
youtube_refresh_token=YOUR_REFRESH_TOKEN
```

Uppercase variants (`YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, and `YOUTUBE_REFRESH_TOKEN`) are also supported. Environment values override the corresponding values in `config/youtube.json`, allowing that JSON file to contain only non-secret defaults such as `channel_name`.

The OAuth helper reads the client ID and client secret from `.env` automatically, opens Google's consent screen, and writes the resulting refresh token back to `.env`:

```powershell
python -m youtube.oauth_helper
```

The OAuth flow requires both `youtube.upload` and `youtube.readonly` scopes. The readonly scope is used to resolve and verify the human-readable Channel Name before uploading. If an existing refresh token was created without that scope, run the helper again and approve the additional permission.

### Upload process

The backend exchanges the refresh token for a temporary access token, verifies the requested channel, and uploads the MP4 through the YouTube Data API v3 resumable upload protocol. Access tokens expire after approximately one hour; they are regenerated automatically and do not need to be stored manually.

For Google accounts managing multiple Brand channels, authorize the intended channel/account context and test the first upload with `private` visibility. YouTube's standard `videos.insert` endpoint does not provide a normal target-channel parameter, so the application rejects channel-name mismatches instead of guessing.

# 💰 Cost Philosophy

Monki Labs follows a **free-only philosophy**.

The project prioritizes:

* 🆓 Local and open-source AI models

* 🆓 Free software

* 🆓 Free development tools

* ☁️ Temporary GPU infrastructure when needed

* 🔑 No paid AI APIs

* 🔑 No required paid API keys

* 🔑 No required subscriptions

The goal is to keep the software and AI pipeline free to operate, using temporary GPU infrastructure only when necessary for generation.

---

# 🔄 Completed Workflow

Monki Labs currently supports the following workflow:

```text
Idea

  ↓

AI Prompt

  ↓

AI Video + Audio

  ↓

Final Video

  ↓

YouTube

  ↓

Optional Replay Toggle
```

The developer configures the content and generation settings, starts an episode from the web UI, and can optionally enable replay to continue generating episodes automatically.

---

## 📜 License

Private project.

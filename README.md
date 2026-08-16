# 🐒 Monki Labs

Monki Labs is a fully automated AI video generation pipeline designed to create short-form vertical videos with minimal human interaction.

The project is designed around **local and cloud GPU execution**, with the long-term goal of automatically generating and publishing high-quality videos on a recurring schedule.

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
│   ├── providers/
│   ├── prompt_generator.py
│   └── video_generator.py
│
├── core/
│   ├── config_loader.py
│   ├── hardware_detector.py
│   ├── logger.py
│   └── pipeline.py
│
├── config/
│   ├── studio.json
│   ├── content.json
│   ├── ai_models.json
│   ├── audio.json
│   └── youtube.json
│
├── media/
│   └── output/
│
├── requirements.txt
├── requirements-pytorch.txt
├── install.bat
├── install.sh
├── run.bat
├── run_linux
├── main.py
└── README.md
```

---

# 💻 Local Setup

Monki Labs is developed locally on Windows using Python 3.12.

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
.\install.bat
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

Once installation is complete:

```powershell
.\run.bat
```

You can also run the application manually:

```powershell
.\.venv\Scripts\activate
python main.py
```

---

## 4. Development Workflow

The normal development workflow is:

```text
Edit code
   ↓
.\run.bat
   ↓
Review generated video
   ↓
Make changes
   ↓
.\run.bat
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
    └── Viral Brainrot/
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
bash install.sh
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
bash run_linux
```

The Linux runner:

* Starts Ollama as a CPU-only process
* Keeps the GPU available for Monki Labs
* Configures PyTorch CUDA memory handling
* Runs the main pipeline

No application code changes are required to run the pipeline on Linux.

---

## 4. Temporary GPU Environments

RunPod instances can be treated as temporary compute environments.

The repository contains the application and configuration, while generated videos can be retrieved before terminating the instance.

The long-term goal is to use temporary GPU infrastructure only when video generation is required rather than maintaining a continuously running server.

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

# 🎞️ Single or Multiple Prompts

The pipeline supports a configurable number of prompts per episode.

With **one prompt**, the model generates one continuous video.

With **multiple prompts**, each prompt generates a separate video segment and the segments are combined into one final `episode.mp4`.

The architecture intentionally retains this flexibility so the number of prompts can be increased later if longer or more complex videos require multiple generated segments.

Regardless of the number of prompts, the final episode remains a single video file.

---

# 📦 Output Retention

Each generation creates a unique run directory:

```text
media/output/
└── <Category Name>/
    └── 001/
        ├── prompt.txt
        └── episode.mp4
```

The system retains:

* `prompt.txt` — the exact prompt or prompts used for generation
* `episode.mp4` — the final generated video

Intermediate video clips and temporary generation files are removed after successful processing.

When multiple prompts are used, they are stored together in the same `prompt.txt` file with a consistent structure and separator between prompts.

This keeps each generation self-contained while avoiding unnecessary storage of intermediate files.

---

# 🧪 Development Status

## ✅ Currently Working

* Configuration-driven pipeline
* Local LLM prompt generation
* Ollama integration
* LTX-2.3 video generation
* Video + background music + sound effects generation
* Configurable video duration
* Configurable generation resolution
* Configurable inference steps
* Configurable guidance settings
* Vertical 9:16 output
* Single-prompt generation
* Multi-prompt / multi-clip architecture
* Automatic final video assembly
* Prompt retention
* Final video retention
* Automatic output organization
* Windows installation
* Linux / GPU installation
* RunPod-compatible execution

## 🚧 Current Focus

* 🎥 Improving generated video quality
* 🔍 Testing generation resolution and inference settings
* 🎬 Improving prompt quality and visual clarity
* ⚡ Optimizing GPU memory usage
* ⏱️ Testing longer video durations

## 🔮 Future Goals

* 🎥 Consistently higher-quality video generation
* 📺 Automated YouTube uploading
* 📂 Playlist management
* ⏰ Scheduled generation
* ☁️ Automated cloud GPU execution
* 🤖 Fully unattended content generation
* 📅 Recurring automated publishing

---

# ☁️ Long-Term Automation

The ultimate goal is for Monki Labs to operate without requiring the developer's PC to remain running.

The intended workflow is:

```text
Scheduled Trigger
       ↓
Cloud GPU Environment
       ↓
Clone / Update Repository
       ↓
Run Monki Labs
       ↓
Generate Prompt
       ↓
Generate Video + Audio
       ↓
Retain Final Video + Prompt
       ↓
Upload to YouTube
       ↓
Terminate GPU Environment
```

The application is intentionally being developed so the same pipeline can run locally for development and later on temporary cloud GPU infrastructure for production generation.

---

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

# 🔮 Vision

Monki Labs is ultimately intended to become an automated content studio:

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
Scheduled Repeat
```

The developer should only need to configure the system and monitor the results.

Everything else should eventually happen automatically.

---

## 📜 License

Private project.

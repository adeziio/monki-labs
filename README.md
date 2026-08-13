# 🐒 Monki Labs

Monki Labs is a fully automated AI video generation pipeline designed to create short-form vertical videos with minimal human interaction.

The project is designed around **local and cloud GPU execution**, with the long-term goal of automatically generating and publishing high-quality videos on a recurring schedule.

---

## 🎯 Goals

Monki Labs aims to:

* 🤖 Automatically generate video concepts using a local language model
* 🎬 Generate short-form AI videos from those concepts
* 🎵 Add music and audio automatically
* 📱 Produce vertical 9:16 videos optimized for short-form platforms
* 📦 Organize generated videos automatically by content category and run
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
Video Concept Generation
        ↓
Wan Video Generation
        ↓
Video Processing
        ↓
Music / Audio
        ↓
Final MP4
        ↓
Organized Output
```

The application is **configuration-driven**, allowing content and AI settings to be changed without modifying the core pipeline.

---

## 🛠️ Tech Stack

### AI

* 🧠 Ollama
* 🤖 Qwen 3 8B
* 🎥 Wan 2.1 T2V 1.3B
* 🤗 Hugging Face Diffusers
* 🔥 PyTorch

### Video

* 🎬 MoviePy
* FFmpeg
* ImageIO

### Audio

* 🎵 Pydub
* Local audio assets

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
├── run.sh
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

`run.bat` automatically:

1. Checks that the virtual environment exists
2. Activates the virtual environment
3. Runs `main.py`
4. Reports if Monki Labs exits with an error

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
        │   └── episode.mp4
        ├── 002/
        │   └── episode.mp4
        └── 003/
            └── episode.mp4
```

---

## 5. Updating Dependencies

Project dependencies are separated into:

```text
requirements.txt
requirements-pytorch.txt
```

`requirements.txt` contains the general application dependencies.

`requirements-pytorch.txt` contains the PyTorch packages.

If dependencies change, rerun:

```powershell
.\install.bat
```

The installer will update the virtual environment with the current dependencies.

---

# ☁️ RunPod / Linux Setup

Monki Labs can run on Linux-based GPU environments such as RunPod without changing the application code.

The same repository and `main.py` are used locally and on cloud GPU environments.

## 1. Clone the private repository

Authenticate with GitHub and clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/monki-labs.git
cd monki-labs
```

For a private repository, use a GitHub Personal Access Token with appropriate repository access.

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
bash run.sh
```

This activates the virtual environment and runs:

```bash
python main.py
```

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
* Video output requirements
* AI model selection
* Audio behavior
* YouTube configuration
* Studio-level settings

The application reads the appropriate configuration at runtime.

---

# 🎥 Video Generation

The current pipeline generates short-form vertical videos using Wan 2.1.

Content configuration defines the desired final video characteristics, including:

* Duration
* Aspect ratio
* Output FPS
* Resolution
* Video format

The video model's generation settings are derived from the content requirements where appropriate.

This keeps the desired output specification centralized rather than requiring the same settings to be maintained across multiple configuration files.

---

# 📦 Output Organization

Each execution creates a new output run.

Outputs are automatically organized using the configured content category name:

```text
media/output/
└── <Category Name>/
    ├── 001/
    ├── 002/
    ├── 003/
    └── ...
```

This prevents previous generations from being overwritten and keeps individual runs separated.

---

# 🧪 Development Status

## ✅ Currently Working

* Local Python pipeline
* Configuration-driven architecture
* Local LLM concept generation
* Ollama integration
* Wan 2.1 video generation
* Automatic video duration
* Automatic model resolution calculation
* Vertical 9:16 output
* Video processing
* Music integration
* Automatic output organization
* Windows installation
* Linux / GPU installation
* RunPod-compatible execution

## 🚧 Future Goals

* 🎥 Higher-quality GPU video generation
* 🎞️ 30–60 FPS final output
* ✨ Improved visual quality
* 🎵 Improved audio generation
* 📺 Automated YouTube uploading
* 📂 Playlist management
* ⏰ Scheduled generation
* ☁️ Automated cloud GPU execution
* 🏃 Kaggle-based GPU execution
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
Generate Video
       ↓
Process Video
       ↓
Upload to YouTube
       ↓
Terminate GPU Environment
```

The application is intentionally being developed so the same pipeline can run locally for development and later on temporary cloud GPU infrastructure for production generation.

---

# 💰 Cost Philosophy

Monki Labs follows a **free-first philosophy**.

The project prioritizes:

* 🆓 Local and open-source AI models
* 🆓 Free software
* 🆓 Free development tools
* 🆓 Free or low-cost infrastructure
* ☁️ Temporary GPU usage instead of always-on servers
* 🔑 Avoiding paid AI APIs and unnecessary subscriptions

The goal is to keep the entire content-generation pipeline as close to **$0 operating cost** as realistically possible.

---

# 🔮 Vision

Monki Labs is ultimately intended to become an automated content studio:

```text
Idea
 ↓
AI Concept
 ↓
AI Video
 ↓
Audio
 ↓
Processing
 ↓
Quality Output
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

# 🐒 Monki Labs

**Monki Labs** is a local, open-source AI animation studio designed to automate the creation of short-form cartoon episodes.

The project combines locally running AI models with a structured character, story, storyboard, image, animation, audio, and video pipeline.

The long-term goal is to create an automated cartoon production system capable of generating complete episodes with **consistent characters, visual storytelling, physical comedy, music, sound effects, and repeatable production workflows**.

---

# ✨ Core Features

## 🎬 Automated Episode Pipeline

Monki Labs is designed around an end-to-end production pipeline:

```text
Episode Idea
      ↓
Story Generation
      ↓
Storyboard Generation
      ↓
Character-Aware Scene Generation
      ↓
Animation Generation
      ↓
Audio Generation
      ↓
Video Assembly
      ↓
Thumbnail Generation
```

The pipeline is built so individual stages can be developed and improved independently.

---

# 🧠 AI Story Generation

Story ideas are generated locally using **Ollama**.

Stories are generated according to the configured series and character rules.

The current story structure includes:

* Concept
* Hook
* Setup
* Escalation
* Ending
* Characters

Example:

```json
{
    "concept": "Max and his friends get lost in the woods",
    "hook": "Max accidentally leaves his favorite snack behind",
    "setup": "Max tries to find his way back home",
    "escalation": "The situation becomes increasingly chaotic",
    "ending": "The characters escape with a comedic resolution",
    "characters": [
        "maxmonkey",
        "sidsquirrel"
    ]
}
```

The system is designed specifically for **silent cartoon storytelling**.

Characters do not require dialogue or narration to communicate the story.

---

# 🎞️ Storyboard Generation

The generated story is converted into a structured storyboard.

Each storyboard scene contains:

* Scene number
* Purpose
* Characters
* Scene description

Example:

```json
{
    "scene": 1,
    "purpose": "Hook",
    "characters": [
        "maxmonkey",
        "sidsquirrel"
    ],
    "description": "Max accidentally leaves his favorite snack behind"
}
```

The storyboard acts as the bridge between the narrative system and visual generation.

---

# 🐒 Character System

Characters are defined through configuration rather than hardcoded into the image-generation system.

Each character can define:

* Name
* Species
* Role
* Series
* Importance
* LoRA model
* Trigger word
* Appearance
* Clothing
* Personality
* Behavior rules
* Story rules
* Visual consistency rules

Characters are identified using unique IDs.

Example:

```text
maxmonkey
sidsquirrel
lialynx
```

This allows new characters to be added without rewriting the image-generation pipeline.

---

# 🎨 Character LoRA System

Monki Labs uses **FLUX LoRA models** to provide character-specific visual consistency.

Each character has its own trained LoRA.

Current characters include:

### 🐒 Max the Monkey

* Brown fluffy fur
* Small, round body
* Blue hoodie
* Red baseball cap
* Large expressive eyes
* Curious and playful personality

LoRA:

```text
models/loras/maxmonkey/
└── maxmonkey_flux_lora_v3.safetensors
```

### 🐿️ Sid the Squirrel

* Light orange fur
* Character-specific clothing
* Designed as one of Max's recurring friends
* Silent physical-comedy character

LoRA models are stored under:

```text
models/loras/sidsquirrel/
```

### 🐆 Lia the Lynx

* Cream-white fur
* Pink hoodie
* Feminine cartoon features
* Girly eyelashes
* Daisy flower accessory
* Recurring character in the Max universe

LoRA models are stored under:

```text
models/loras/lialynx/
```

Additional characters can be added using the same structure.

---

# 🧪 LoRA Training

Character LoRAs are trained locally using **FLUX.1-schnell** and AI Toolkit.

The character training workflow uses a curated dataset of high-quality character images and matching text captions.

The current approach focuses on **quality over dataset size** rather than generating large numbers of redundant training images.

The training workflow includes:

* Character-specific datasets
* Caption files
* Multiple resolution buckets
* LoRA training
* Periodic checkpoints
* Sample generation during training
* Final LoRA models for production generation

Example dataset:

```text
datasets/
└── maxmonkey/
    ├── image_001.png
    ├── image_001.txt
    ├── image_002.png
    ├── image_002.txt
    └── ...
```

---

# 🖼️ FLUX Image Generation

Monki Labs uses:

```text
black-forest-labs/FLUX.1-schnell
```

through Hugging Face Diffusers.

Character LoRAs are loaded into the FLUX pipeline to generate character-specific images.

The system supports:

* Local FLUX generation
* Character-specific LoRAs
* Custom prompts
* Configurable image dimensions
* Configurable inference steps
* CUDA acceleration
* CPU fallback

---

# 🧪 Ad-Hoc Character Image Generator

A standalone image-generation tool is available for testing characters independently of the full episode pipeline.

```text
tools/generate_image.py
```

The tool automatically discovers available character LoRAs from:

```text
models/loras/
```

Example:

```text
Available Characters:

1. maxmonkey
2. sidsquirrel
3. lialynx
```

After selecting a character, available LoRA versions are displayed.

This makes it possible to test:

* Character appearance
* Expressions
* Poses
* Clothing
* Environments
* Prompt behavior
* LoRA versions

without generating an entire episode.

---

# 🎭 Silent Cartoon Philosophy

Monki Labs is designed around a **dialogue-free cartoon format**.

Characters:

* Never speak
* Do not use dialogue
* Do not require narration
* Communicate through movement
* Communicate through facial expressions
* Use physical comedy

The intended style is inspired by classic visual-comedy cartoons such as **Tom and Jerry**, where the story can be understood primarily through animation, music, timing, and sound effects.

Comedy should come from:

* Character reactions
* Physical movement
* Misunderstandings
* Escalating situations
* Cartoon physics
* Visual surprises
* Music and sound effects

---

# 🌎 Series System

The current universe is:

## Max the Monkey Adventures

A family-friendly 3D animated cartoon universe centered around Max and his friends.

### Genre

* Comedy
* Adventure

### Audience

* Family
* Everyone

### Format

* YouTube Shorts
* 30–60 seconds
* 9:16 vertical video

### Visual Style

* 3D animated cartoon
* Bright colors
* Expressive characters
* Cinematic lighting
* Cartoon physics
* Family friendly

### World

The primary setting is a colorful cartoon jungle.

Possible locations include:

* Jungle
* Treehouse
* River
* Caves
* Hidden areas

---

# 🔊 Audio

The animation style intentionally avoids dialogue.

Audio is instead built around:

* Background music
* Sound effects
* Comedic timing
* Suspense
* Character movement
* Environmental sounds

The current series configuration supports mood-based music selection such as:

```text
Funny      → comedy.mp3
Adventure  → adventure.mp3
Chaotic    → suspense.mp3
```

---

# 🎥 Animation

The animation stage is designed to convert generated scene images into animated sequences.

The project currently includes an animation provider architecture with support for:

* Local animation models
* CUDA acceleration
* CPU fallback
* MoviePy-based fallback processing

The animation system is still under active development.

---

# 🖥️ Hardware Support

Monki Labs detects available hardware automatically.

Supported execution modes include:

| Hardware          | Support                    |
| ----------------- | -------------------------- |
| CPU               | ✅                          |
| NVIDIA CUDA GPU   | ✅                          |
| CPU fallback      | ✅                          |
| Apple Silicon MPS | ⚠️ Configuration dependent |

When CUDA is unavailable, the system can fall back to CPU processing.

Example:

```text
Running on device: cpu
```

or:

```text
Running on device: cuda
```

AI generation is significantly faster with a compatible NVIDIA GPU.

---

# 🆓 Free-Only Philosophy

Monki Labs is designed to remain **free to run from a software/API perspective**.

The project does not rely on paid external AI APIs or subscription-based AI services.

The intended architecture prioritizes:

* Local AI models
* Open-source libraries
* Local inference
* Local model files
* Local processing

Hardware requirements and model storage requirements still apply.

---

# ⚙️ Configuration

Monki Labs uses JSON configuration files rather than embedding project behavior directly into the code.

Current configuration includes:

```text
config/
├── settings.json
├── series.json
├── characters.json
├── ai_models.json
├── pipeline.json
├── audio.json
├── youtube.json
└── studio.json
```

### `characters.json`

Defines the characters and their identities.

Controls:

* Appearance
* Clothing
* Personality
* Behavior
* Story rules
* LoRA paths
* Trigger words

### `series.json`

Defines the series itself.

Controls:

* Genre
* Audience
* Episode format
* Animation style
* Visual style
* World rules
* Tone
* Audio behavior

### `ai_models.json`

Defines AI model providers and model locations.

Controls:

* Language model
* Image model
* Image LoRA
* Animation model
* Audio system

### `settings.json`

Defines global execution and output settings.

Controls:

* Local environment
* Free-only operation
* Execution mode
* CPU fallback
* Output format
* Resolution
* FPS

---

# 📁 Project Structure

```text
monki-labs/

├── ai/
│   ├── providers/
│   │   ├── flux_provider.py
│   │   └── ollama_provider.py
│   │
│   ├── story_generator.py
│   ├── storyboard_generator.py
│   ├── image_generator.py
│   ├── animation_generator.py
│   ├── audio_generator.py
│   ├── thumbnail_generator.py
│   └── video_builder.py
│
├── characters/
│   └── character_manager.py
│
├── config/
│   ├── settings.json
│   ├── series.json
│   ├── characters.json
│   ├── ai_models.json
│   ├── pipeline.json
│   ├── audio.json
│   ├── youtube.json
│   └── studio.json
│
├── core/
│   ├── pipeline.py
│   ├── config_loader.py
│   ├── hardware_detector.py
│   ├── episode_manager.py
│   └── logger.py
│
├── models/
│   └── loras/
│       ├── maxmonkey/
│       ├── sidsquirrel/
│       └── lialynx/
│
├── datasets/
│   ├── maxmonkey/
│   ├── sidsquirrel/
│   └── lialynx/
│
├── media/
│   ├── adhoc/
│   └── series/
│
├── tools/
│   └── generate_image.py
│
├── main.py
├── install.bat
└── run.bat
```

---

# 📦 Episode Output

Generated episodes are organized by series and episode.

Example:

```text
media/
└── series/
    └── max_the_monkey/
        └── ep_0001/
            ├── scenes/
            │   ├── scene_001.png
            │   ├── scene_002.png
            │   ├── scene_003.png
            │   └── scene_004.png
            │
            ├── video/
            │
            ├── story.json
            └── storyboard.json
```

This structure keeps each episode's generated assets isolated and reproducible.

---

# 🚀 Installation

## Requirements

* Python 3.12+
* FFmpeg
* Windows currently optimized
* NVIDIA GPU recommended for AI image generation
* Sufficient disk space for local AI models

---

## Quick Start

Clone the repository:

```bash
git clone <repository-url>
cd monki-labs
```

Run the installer:

```bash
install.bat
```

The installer is intended to:

* Create the Python environment
* Install dependencies
* Configure PyTorch
* Detect NVIDIA hardware
* Verify FFmpeg
* Prepare the project environment

Start the application:

```bash
run.bat
```

---

# 🧪 Development Tools

### Test Character Generation

Run:

```bash
python tools/generate_image.py
```

The tool allows you to select:

1. Character
2. LoRA version
3. Prompt
4. Image dimensions
5. Inference steps
6. Output filename

This is currently the fastest way to validate a newly trained character LoRA before integrating it into the episode pipeline.

---

# 🛠️ Development Status

## ✅ Completed / Working

* ✅ Project configuration system
* ✅ Hardware detection
* ✅ CPU/CUDA execution handling
* ✅ Character configuration system
* ✅ Character manager
* ✅ Character-specific LoRA configuration
* ✅ Max character LoRA
* ✅ Sid character LoRA
* ✅ Lia character LoRA
* ✅ FLUX image generation
* ✅ Ad-hoc character image generation
* ✅ LoRA selection for ad-hoc generation
* ✅ Local Ollama story generation
* ✅ Structured story generation
* ✅ Storyboard generation
* ✅ Character-aware story output
* ✅ Character-aware storyboard output
* ✅ Episode workspace generation
* ✅ Scene image generation foundation
* ✅ Audio pipeline foundation
* ✅ Animation pipeline foundation
* ✅ Video assembly foundation

---

# 🚧 Currently In Development

* 🚧 Multi-character scene generation
* 🚧 Improved visual scene descriptions
* 🚧 Advanced character interaction
* 🚧 Animation quality
* 🚧 Camera movement
* 🚧 Automated sound-effect generation
* 🚧 Improved audio synchronization
* 🚧 Final video quality pipeline
* 🚧 Thumbnail generation improvements
* 🚧 YouTube publishing automation

---

# 🗺️ Development Direction

The immediate development direction is:

```text
Character LoRAs
      ↓
Character-Aware Stories
      ↓
Character-Aware Storyboards
      ↓
Multi-Character Scene Generation
      ↓
Character Animation
      ↓
Music + Sound Effects
      ↓
Final Video
      ↓
Automated Publishing
```

The most important current focus is **character consistency and multi-character interaction**.

The system should ultimately be able to take a story such as:

```text
Max and Sid get lost in the jungle.
```

and automatically determine:

* Which characters appear in each scene
* What each character is doing
* How they interact
* Their expressions
* Their poses
* Their environment
* The visual composition
* The animation required
* The appropriate music and sound effects

---

# 🎯 Project Vision

The long-term goal of Monki Labs is to create a **local, automated AI animation studio** capable of producing entire cartoon series.

The system should eventually handle the complete production process:

```text
Idea
 ↓
Story
 ↓
Characters
 ↓
Storyboard
 ↓
Images
 ↓
Animation
 ↓
Music
 ↓
Sound Effects
 ↓
Video
 ↓
Thumbnail
 ↓
Publishing
```

The goal is not simply to generate AI images.

**The goal is to build an automated cartoon production system.**

---

# 🤝 Contributing

Contributions, ideas, experiments, and improvements are welcome.

Potential contribution areas include:

* AI model integrations
* Character systems
* LoRA training
* Animation
* Audio
* Video processing
* Performance optimization
* Production automation

---

# 📜 License

License information coming soon.

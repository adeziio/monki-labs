# 🐒 Monki Labs

AI-powered animation studio for creating automated cartoon episodes.

Monki Labs is an open-source pipeline designed to generate complete animated episodes from an idea.

The goal is to build a fully automated AI animation pipeline capable of producing short-form cartoon content with consistent characters and a repeatable production workflow.

---

# ✨ Features

## 🎬 Automated Episode Pipeline

Monki Labs manages the entire episode workflow:

```
Episode Idea
      ↓
Story Generation
      ↓
Storyboard Generation
      ↓
Scene Image Generation
      ↓
Animation Pipeline
      ↓
Audio Generation
      ↓
Video Assembly
      ↓
Thumbnail Generation
```

---

## 🧠 AI Story Generation

Generates episode concepts and story structures based on configured series rules.

Supports:

- Episode hooks
- Story setup
- Escalation
- Ending twists
- Character-driven stories

---

## 🎨 Character Consistency System

Characters are defined through configuration instead of hardcoded logic.

Example:

```
characters/
├── characters.json
└── references/
```

Characters include:

- Appearance
- Clothing
- Personality
- Behavior rules
- Story rules
- Visual references

Example character:

## Max the Monkey

- Small cartoon monkey
- Brown fluffy fur
- Blue hoodie
- Red baseball cap
- No dialogue
- Communicates through facial expressions and physical comedy

---

## 🖼️ AI Image Generation

Uses local Stable Diffusion generation through Hugging Face Diffusers.

Features:

- Local AI generation
- Character reference images
- Negative prompts
- Configurable models
- CPU/GPU support

Generated scenes are stored per episode:

```
media/
└── series/
    └── max_the_monkey/
        └── ep_0001/
            ├── scenes/
            ├── video/
            ├── story.json
            └── storyboard.json
```

---

## 🔊 Audio Pipeline

Supports:

- Background music
- Sound effect planning
- No-dialogue animation style

The current animation style focuses on visual storytelling inspired by classic physical comedy cartoons.

---

## 🎥 Video Assembly

Combines:

- Generated scenes
- Animation outputs
- Audio tracks

into final MP4 episodes.

---

# 🖥️ Hardware Support

Monki Labs automatically detects available hardware.

Supported:

| Hardware | Support |
|---|---|
| CPU | ✅ |
| NVIDIA GPU | ✅ |
| Apple Silicon MPS | ✅ |

GPU acceleration is automatically enabled when available.

Example:

```
Running on device: cpu
```

or:

```
Running on device: cuda
```

---

# 🚀 Installation

## Requirements

- Python 3.12+
- FFmpeg
- Windows (currently optimized)

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

The installer automatically:

- Creates a Python virtual environment
- Installs dependencies
- Detects NVIDIA GPUs
- Installs the correct PyTorch version
- Checks FFmpeg
- Verifies the installation

Start Monki Labs:

```bash
run.bat
```

---

# 📁 Project Structure

```
monki-labs/

├── ai/
│   ├── providers/
│   ├── story_generator.py
│   ├── storyboard_generator.py
│   ├── image_generator.py
│   ├── audio_generator.py
│   └── video_builder.py
│
├── characters/
│   ├── characters.json
│   └── references/
│
├── config/
│   ├── settings.json
│   ├── series.json
│   ├── audio.json
│   └── ai_models.json
│
├── core/
│   ├── pipeline.py
│   ├── hardware_detector.py
│   ├── episode_manager.py
│   └── config_loader.py
│
├── media/
│   └── series/
│
├── install.bat
├── run.bat
└── main.py
```

---

# ⚙️ Configuration

Monki Labs uses JSON configuration files.

## Series Configuration

Controls:

- Genre
- Audience
- Episode structure
- Visual style
- World rules

File:

```
config/series.json
```

---

## Character Configuration

Controls:

- Appearance
- Personality
- Behavior
- Visual consistency

File:

```
characters/characters.json
```

---

## AI Model Configuration

Controls:

- AI models
- Providers
- Output locations

File:

```
config/ai_models.json
```

---

# 🐒 Current Series

## Max the Monkey Adventures

A family-friendly cartoon series built around physical comedy.

Rules:

- No dialogue
- Expressive animation
- Cartoon physics
- Comedy-driven stories

Style:

- 3D animated cartoon
- Bright colors
- Cinematic scenes
- Expressive characters

---

# 🛠️ Development Roadmap

## Completed

✅ Automated episode pipeline  
✅ Story generation  
✅ Storyboard generation  
✅ Character configuration system  
✅ Character reference loading  
✅ Stable Diffusion scene generation  
✅ Audio pipeline foundation  
✅ Video assembly  
✅ Hardware detection  
✅ One-click installation  

---

## In Progress

🚧 AI motion generation  
🚧 Advanced animation pipeline  
🚧 Better camera movement  
🚧 Automated sound effects  
🚧 Improved character consistency  
🚧 YouTube publishing automation  

---

# 🎯 Project Vision

The long-term goal of Monki Labs is to create an automated AI animation studio capable of producing complete animated series with:

- Consistent characters
- Automated storytelling
- AI-generated animation
- Music and sound design
- Video publishing workflows

The goal is not just generating images, but building an end-to-end creative production system.

---

# 🤝 Contributing

Contributions, ideas, and experiments are welcome.

Potential contribution areas:

- AI model integrations
- Animation improvements
- Audio systems
- Character tools
- Performance optimization

---

# 📜 License

License information coming soon.
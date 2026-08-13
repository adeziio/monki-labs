# 🐒 Monki Labs

**Monki Labs** is a fully automated, local-first AI video generation pipeline built to create and eventually publish short-form YouTube content with minimal human involvement.

The long-term goal is simple:

> **Generate → Process → Publish → Repeat**

---

## 🚀 Vision

Monki Labs is being built as an automated AI content studio capable of:

* 💡 Generating original video concepts
* 🤖 Creating AI-generated video
* 🎬 Processing and assembling footage
* 🎵 Adding audio
* 🖼️ Generating supporting content such as thumbnails
* 📤 Uploading videos to YouTube
* ⏰ Publishing automatically on a recurring schedule
* ☁️ Running on remote GPU infrastructure without requiring a personal computer to stay powered on

The ultimate goal is a **fully unattended weekly content pipeline**.

---

## 🎬 Current Pipeline

The current system can generate a complete short-form video from start to finish.

```text
💡 Content Generation
        ↓
🧠 Local LLM
        ↓
🎥 AI Video Generation
        ↓
✂️ Clip Processing
        ↓
🎵 Audio
        ↓
🎞️ Final Video
        ↓
📁 Organized Output
```

The pipeline currently produces vertical short-form videos designed for platforms such as YouTube Shorts.

---

## ✨ Current Capabilities

* 🧠 Local AI-powered concept generation
* 🎥 AI text-to-video generation
* 📱 Vertical 9:16 video output
* ⏱️ Configurable short-form duration
* 🎬 Automatic clip generation and processing
* 🎵 Optional background music
* 📂 Organized output by content category and generation run
* ⚙️ Configuration-driven behavior
* 🖥️ Local CPU/GPU execution
* 🔄 Modular pipeline designed for future automation

---

## 🤖 AI Stack

### Language Model

* **Ollama**
* **Qwen3 8B**

Used to generate original short-form video concepts and prompts.

### Video Generation

* **Wan 2.1 T2V 1.3B**
* **Hugging Face Diffusers**
* **PyTorch**

Used to turn generated concepts into AI video clips.

---

## 🛠️ Technology Stack

| Technology   | Purpose                |
| ------------ | ---------------------- |
| 🐍 Python    | Core application       |
| 🧠 Ollama    | Local LLM execution    |
| 🤖 Qwen3 8B  | Concept generation     |
| 🎥 Wan 2.1   | AI video generation    |
| 🔥 PyTorch   | Model execution        |
| 🤗 Diffusers | AI model pipelines     |
| 🎬 MoviePy   | Video processing       |
| 🎞️ FFmpeg   | Video/audio processing |

---

## 😂 Content Direction

The initial content focus is **viral visual comedy**.

The system is designed around concepts that are:

* ⚡ Fast-paced
* 😂 Visually funny
* 🤯 Unexpected
* 🌀 Absurd
* 👀 Immediately interesting
* 🎬 Easy to understand without dialogue
* 🔄 Independent from other videos

Example concepts include unusual physical events, impossible situations, unexpected object behavior, strange machines, and other forms of visual comedy.

The pipeline is designed to eventually support multiple content categories without rebuilding the core system.

---

## ⚙️ Design Principles

### 🆓 Free-First

The project is designed around free and locally available tools whenever possible.

The goal is to avoid unnecessary:

* Paid AI APIs
* Subscription services
* API keys
* Recurring infrastructure costs

### 🧩 Config-Driven

Project behavior should be controlled through configuration rather than unnecessary hard-coded values.

This makes it easier to change content requirements, models, and generation behavior without modifying the core pipeline.

### 🤖 Automation-First

Manual interaction should be minimized.

The long-term goal is for the system to generate and publish content without requiring the user to manually start the process.

### 🧱 Modular

Individual components should be replaceable without requiring the entire application to be rewritten.

### ☁️ Remote-Ready

Although development currently happens locally, the system is being built with eventual remote GPU execution in mind.

---

## ☁️ Future Deployment

The eventual goal is to move video generation to a remote GPU environment.

Instead of requiring a personal computer to remain powered on:

```text
⏰ Scheduled Trigger
        ↓
☁️ Remote GPU
        ↓
🧠 Generate Concept
        ↓
🎥 Generate Video
        ↓
🎵 Process Audio
        ↓
🎞️ Create Final Video
        ↓
📤 Upload to YouTube
        ↓
📅 Publish
```

The target is approximately **one high-quality video per week**, while taking advantage of free GPU resources where practical.

---

## 📊 Project Status

### ✅ Completed

* [x] Configuration-driven pipeline
* [x] Local LLM integration
* [x] AI video generation
* [x] Dynamic video generation settings
* [x] 9:16 vertical video generation
* [x] Configurable video duration
* [x] Automatic clip processing
* [x] Audio integration
* [x] Organized generation outputs
* [x] End-to-end video generation successfully tested

### 🚧 In Progress

* [ ] Improve AI video quality
* [ ] Improve generation speed
* [ ] Optimize GPU execution
* [ ] Improve concept generation
* [ ] Thumbnail generation
* [ ] YouTube integration
* [ ] Remote GPU deployment
* [ ] Automated scheduling

### 🔮 Long-Term Goals

* [ ] Fully unattended weekly publishing
* [ ] Remote execution without a personal computer
* [ ] Multiple content categories
* [ ] Automated quality control
* [ ] Automated thumbnail generation
* [ ] Automated YouTube uploads
* [ ] Automated publishing and scheduling
* [ ] End-to-end autonomous content pipeline

---

## 🐒 The Goal

Monki Labs isn't just a video generator.

The goal is to build a **small automated AI content studio** capable of continuously creating, processing, and publishing short-form content with minimal human involvement.

**Generate. Automate. Publish. Repeat.** 🚀

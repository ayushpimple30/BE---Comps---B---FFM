<!--
FFM Sentinel — Project README
GitHub README supports Markdown, Mermaid, and limited HTML.
Animations are provided by an external SVG service; GitHub does not run custom CSS or JavaScript here.
-->

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=34&duration=2800&pause=900&color=39D0FF&center=true&vCenter=true&width=850&height=70&lines=FFM+SENTINEL;Your+Intelligent+AI+Companion;Local+AI.+Real-World+Interaction." alt="Animated FFM Sentinel title" />

<p><strong>OFFLINE MULTIMODAL AI COMPANION FOR INTERACTIVE ASSISTANCE</strong></p>

<p>
  A final-year engineering project exploring local AI, multimodal interaction, and embedded computing.
</p>

<p>
  <img src="https://img.shields.io/badge/PROJECT-FINAL%20YEAR-172554?style=for-the-badge&labelColor=0B1220" alt="Final-year project" />
  <img src="https://img.shields.io/badge/DOMAIN-ARTIFICIAL%20INTELLIGENCE-6D28D9?style=for-the-badge&labelColor=0B1220" alt="Artificial intelligence" />
  <img src="https://img.shields.io/badge/PLATFORM-RASPBERRY%20PI-C2410C?style=for-the-badge&logo=raspberrypi&logoColor=white&labelColor=0B1220" alt="Raspberry Pi" />
  <img src="https://img.shields.io/badge/STATUS-IN%20DEVELOPMENT-D97706?style=for-the-badge&labelColor=0B1220" alt="In development" />
</p>

<p>
  <a href="#-overview">Overview</a> •
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-setup">Setup</a> •
  <a href="#-team">Team</a>
</p>

</div>

---

## ◈ Overview

**FFM Sentinel (Friendly Functional Machine)** is a final-year engineering project focused on building an interactive AI companion by combining AI software, multimodal inputs, and embedded computing.

The project explores the use of locally hosted AI models and hardware-assisted interaction. Its goal is to make AI interaction more self-contained where supported by the configured models, software, and hardware.

> **Project principle:** Document what has been implemented, test what is claimed, and keep the system understandable and reproducible.

## ◈ The Problem

Many AI-powered experiences depend on remote services, internet connectivity, or external infrastructure. These dependencies can introduce connectivity constraints, recurring service costs, and privacy considerations.

FFM Sentinel investigates a compact alternative that brings AI inference and supported input/output devices together in a single interactive system.

## ◈ Project Objectives

- Integrate locally hosted AI models into an interactive application.
- Explore multimodal interaction through supported input devices.
- Connect application software with embedded hardware.
- Investigate local inference and offline operation.
- Document system design, setup, limitations, and test results.
- Evaluate the implementation using repeatable functional tests.

## ◈ Features

The list below describes the intended areas of the project. Mark a capability as complete only after testing it in the current implementation.

| Area | Purpose |
|---|---|
| 🧠 Local AI inference | Run configured AI models through a local runtime |
| 👁️ Visual input | Process camera input when the vision module is enabled |
| 🎙️ Audio interaction | Support microphone or speech features when implemented |
| 💬 Response interface | Present generated responses through available output modules |
| 🔩 Hardware integration | Connect the application to the target computing platform and peripherals |
| 🔒 Local-first direction | Reduce cloud dependence where the full workflow supports local operation |

## ◈ Architecture

The diagram below shows the **conceptual system flow**. Update the blocks and connections to match the modules actually present in the codebase.

```mermaid
flowchart TD
    U["User"] --> IN["Input Layer"]
    CAM["Camera"] --> IN
    MIC["Microphone"] --> IN

    IN --> PRE["Input Processing"]
    PRE --> AI["AI Orchestration"]
    AI --> LLM["Language Model"]
    AI --> VLM["Vision Model"]
    LLM --> RESP["Response Handling"]
    VLM --> RESP

    RESP --> TXT["Text / Display Output"]
    RESP --> AUD["Speech / Audio Output"]

    HW["Embedded Computing Platform"] --- PRE
    HW --- AI

    classDef source fill:#102A43,stroke:#39D0FF,color:#FFFFFF,stroke-width:1.5px
    classDef process fill:#211A45,stroke:#A78BFA,color:#FFFFFF,stroke-width:1.5px
    classDef output fill:#12372A,stroke:#34D399,color:#FFFFFF,stroke-width:1.5px
    class U,CAM,MIC source
    class IN,PRE,AI,LLM,VLM,RESP process
    class TXT,AUD output
```

### Architecture layers

1. **Input layer** — receives supported user input from connected devices.
2. **Processing layer** — prepares input for the appropriate module.
3. **AI layer** — invokes the configured language or vision model.
4. **Response layer** — formats the result for the supported output interface.
5. **Hardware layer** — supplies the compute platform and peripheral connections.

## ◈ Technology Stack

| Component | Planned / possible technology |
|---|---|
| Embedded computer | Raspberry Pi 5 |
| Local model runtime | Ollama |
| Language model | Gemma 3, if configured |
| Vision model | Moondream 2, if configured |
| Application language | Python, where used |
| Version control | Git and GitHub |

These are not claims that every component is currently integrated. The final stack should match the working implementation and installed versions.

## ◈ Hardware

The prototype configuration may include:

- Raspberry Pi 5
- Raspberry Pi Camera Module
- USB microphone
- External speaker
- Touchscreen display
- Compatible power supply and storage
- Additional controllers, switches, and accessories as required

Record the exact components used in the final build in the project documentation.

## ◈ Setup

### Prerequisites

- Git
- Python version required by the project
- Project dependencies
- Ollama and required model files, if used
- Compatible hardware for hardware-dependent features

### 1. Clone the repository

```bash
git clone https://github.com/ayushpimple30/BE---Comps---B---FFM.git
cd BE---Comps---B---FFM
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

**Windows (Command Prompt):**

```bat
.venv\Scripts\activate
```

**Linux / Raspberry Pi OS:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

If the repository contains a `requirements.txt` file:

```bash
python -m pip install -r requirements.txt
```

### 4. Configure models

If Ollama is part of the implementation, install it and download the exact models required by the application. For example, only if these model names match your configuration:

```bash
ollama pull gemma3
ollama pull moondream
```

### 5. Run the application

Use the actual entry-point file and run instructions from the source code:

```bash
python YOUR_ENTRY_POINT.py
```

Replace `YOUR_ENTRY_POINT.py` with the real script name. Additional hardware configuration may be required.

## ◈ Repository Guide

Use this as a documentation target, not as a claim that these exact folders already exist.

```text
BE---Comps---B---FFM/
├── README.md
├── requirements.txt
├── .gitignore
├── src/                 # Application source code
├── docs/                # Architecture and technical documentation
├── assets/
│   ├── diagrams/        # System diagrams
│   └── screenshots/     # Actual implementation screenshots
└── tests/               # Functional tests, where available
```

## ◈ Implementation Evidence

Use this section to demonstrate the work completed—not just the planned design.

For each implemented feature, add:
- A genuine screenshot or prototype photograph
- The test input and expected behaviour
- The observed output
- Pass/fail status
- Relevant limitations or known issues

Suggested evidence to include:

| Evidence | What it demonstrates |
|---|---|
| Application running | Successful startup |
| Model response | AI integration |
| Camera test | Visual pipeline, if implemented |
| Audio test | Audio pipeline, if implemented |
| Prototype photograph | Hardware assembly |
| Test summary | Repeatable validation results |

Do not publish fabricated screenshots, performance numbers, or test outcomes.

## ◈ Development Roadmap

- [ ] Verify the end-to-end application workflow
- [ ] Validate configured AI models
- [ ] Test implemented input and output modules
- [ ] Verify operation on the target hardware
- [ ] Add actual screenshots and prototype photographs
- [ ] Document functional tests and known limitations
- [ ] Finalise installation instructions and project report

Update this checklist as work is completed.

## ◈ Limitations

Performance depends on available memory, compute capability, model size, dependencies, and the quality of the implementation. Local model inference does not by itself guarantee that every feature works offline; the full application workflow and its dependencies must be tested.

## ◈ Future Scope

- Improve response latency and resource utilisation.
- Expand supported multimodal interaction.
- Strengthen hardware integration and recovery from errors.
- Improve interface usability and accessibility.
- Measure reliability and offline behaviour under repeatable test conditions.

## ◈ Project Team

**Institution:** St. John College of Engineering and Management  
**Programme:** B.Tech  
**Department:** Computer Engineering  
**Project Guide:** Dr. Mahesh Maurya

| Team member | Roll number |
|---|---:|
| Ayush Pimple | 24 |
| Harshal Raut | 34 |
| Shreyash Patil | 18 |
| Sarvesh Patil | 17 |

## ◈ References

- [Python Documentation](https://docs.python.org/3/)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [Ollama Documentation](https://docs.ollama.com/)
- [GitHub Markdown Documentation](https://docs.github.com/en/get-started/writing-on-github)

---

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=18&pause=1200&color=39D0FF&center=true&vCenter=true&width=650&height=40&lines=Built+with+curiosity.;Designed+for+real-world+interaction.;FFM+Sentinel+%E2%80%94+Engineering+intelligence." alt="Animated project sign-off" />

<sub>Final-year engineering project • St. John College of Engineering and Management</sub>

</div>

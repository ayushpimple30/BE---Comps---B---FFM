# FFM Sentinel
### Offline Multimodal AI Companion for Interactive Assistance

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=24&pause=1000&color=00D4FF&center=true&vCenter=true&width=800&lines=Your+Intelligent+AI+Companion;Multimodal+Interaction;Local+AI+%7C+Smart+Hardware+%7C+Innovation" alt="Animated FFM Sentinel introduction" />

<br/>

**An intelligent companion project exploring the integration of local AI, multimodal interaction, and embedded computing.**

<br/>

![Project](https://img.shields.io/badge/Project-Final_Year_Engineering-2563EB?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-Multimodal-7C3AED?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Raspberry_Pi_C23138?style=for-the-badge&logo=raspberrypi&logoColor=white)
![Status](https://img.shields.io/badge/Development-In_Progress-F59E0B?style=for-the-badge)

[Overview](#-overview) · [Features](#-key-features) · [Architecture](#-system-architecture) · [Setup](#-installation-and-setup) · [Team](#-project-team)

</div>

---

## 🌌 Overview

**FFM Sentinel** is a final-year engineering project focused on developing an interactive AI companion that combines artificial intelligence, hardware integration, and user interaction in a unified system.

The project explores the use of locally hosted AI models to support intelligent responses and multimodal interaction, with an emphasis on reducing reliance on cloud-based processing where feasible.

By bringing together software, AI inference, and embedded computing, FFM Sentinel aims to demonstrate how an AI companion can be designed around a compact computing platform.

> **Our vision:** Make AI interaction more accessible, interactive, and practical through the integration of software intelligence and physical computing.

## 🎯 Problem Statement

Many AI-powered interactive systems rely on cloud infrastructure, continuous internet access, or external services. This can introduce connectivity dependencies, privacy considerations, and additional operating costs.

FFM Sentinel investigates an alternative approach by exploring local AI inference and hardware-assisted interaction within a self-contained companion system.

## ✨ Key Features

> Update this section to include only features that are implemented or demonstrably working.

| Feature | Description |
|---|---|
| 🧠 Local AI | Integration with locally hosted AI models, where configured |
| 👁️ Visual Intelligence | Camera-based input and vision-model processing, if implemented |
| 🎙️ Voice Interaction | Audio input and speech processing, if implemented |
| 💬 Interactive Responses | Text or speech output through supported application modules |
| 🔌 Hardware Integration | Integration with compatible embedded hardware and peripherals |
| 🛡️ Offline-Oriented Design | Exploration of local processing to reduce cloud dependencies |

## 🏗️ System Architecture

The following diagram illustrates the intended high-level workflow. The final diagram should be updated to match the modules implemented in the repository.

```mermaid
flowchart TD
    A["🎥 Camera Input"] --> D["Input Processing"]
    B["🎙️ Microphone Input"] --> D
    C["⌨️ User Interaction"] --> D

    D --> E["🧠 AI Processing Layer"]
    E --> F["Local Language Model"]
    E --> G["Vision Model"]

    F --> H["Response Generation"]
    G --> H

    H --> I["🔊 Audio Output"]
    H --> J["💬 Text / Interface Output"]

    K["Embedded Computing Platform"] --- D
    K --- E

    classDef input fill:#102A43,stroke:#00D4FF,color:#FFFFFF
    classDef ai fill:#241547,stroke:#A78BFA,color:#FFFFFF
    classDef output fill:#12372A,stroke:#34D399,color:#FFFFFF

    class A,B,C input
    class D,E,F,G,H ai
    class I,J output
```

### Architecture Layers

- **Input Layer:** Collects supported user inputs from connected devices.
- **Processing Layer:** Prepares inputs for the appropriate processing modules.
- **AI Layer:** Runs the configured language or vision models.
- **Response Layer:** Converts model outputs into supported user-facing responses.
- **Hardware Layer:** Provides the computing environment and peripheral interfaces.

## ⚙️ Technology Stack

The final stack depends on the versions and modules actually used in the project.

| Component | Technology |
|---|---|
| Computing platform | Raspberry Pi 5 |
| AI model runtime | Ollama |
| Language model | Gemma 3, if configured |
| Vision model | Moondream 2, if configured |
| Programming language | Python, where used |
| Input/output | Camera, microphone, speaker and display, as implemented |
| Version control | Git and GitHub |

## 🔩 Hardware Requirements

The intended hardware configuration may include:

- Raspberry Pi 5
- Raspberry Pi Camera Module
- USB microphone
- External speaker
- Touchscreen display
- Compatible power supply
- Additional controllers, switches and accessories as required

The final requirements list should reflect the hardware actually assembled and tested.

## 🚀 Installation and Setup

### Prerequisites

- Python 3.11 or the version specified by the project
- Git
- Required project dependencies
- Ollama and the required models, if used
- Compatible hardware for hardware-dependent features

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/FFM-Sentinel.git
cd FFM-Sentinel
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bat
.venv\Scripts\activate
```

On Linux or Raspberry Pi OS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

If the repository includes a `requirements.txt` file:

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the AI models

If the project uses Ollama, install it and pull the model versions required by the application.

Example commands, only if these models are part of your configuration:

```bash
ollama pull gemma3
ollama pull moondream
```

### 5. Run the application

Use the actual entry-point script from the repository:

```bash
python YOUR_ENTRY_POINT.py
```

Replace `YOUR_ENTRY_POINT.py` with the correct filename before running the command. Hardware-dependent modules may require additional configuration.

## 📂 Project Structure

The following is a suggested structure. Adjust it to match the actual source tree.

```text
FFM-Sentinel/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── main.py
│   ├── ai/
│   ├── vision/
│   ├── audio/
│   └── interface/
│
├── assets/
│   ├── screenshots/
│   ├── diagrams/
│   └── images/
│
├── docs/
│   ├── architecture.md
│   ├── hardware.md
│   └── testing.md
│
└── tests/
```

## 🧪 Implementation and Testing

This section will document the actual implementation and validation of the project.

| Test Area | Evidence to Include |
|---|---|
| Application startup | Screenshot or execution log |
| AI model integration | Sample input and output |
| Vision processing | Test image and observed result, if implemented |
| Audio interaction | Recording or speech test result, if implemented |
| Hardware integration | Photographs of the assembled prototype |
| Error handling | Results of relevant failure tests |

Only report tests that have actually been performed. Add measured latency, accuracy, or other performance figures only when supported by test data.

## 📸 Project Gallery

Add genuine implementation screenshots and photographs here.

```text
assets/
├── screenshots/
│   ├── application.png
│   └── model-output.png
└── images/
    └── prototype.jpg
```

Once uploaded, embed them in this README using relative paths, for example:

```markdown
![Application Screenshot](assets/screenshots/application.png)
```

## 🗺️ Development Roadmap

- [ ] Complete the core application workflow
- [ ] Integrate and validate the required AI models
- [ ] Verify the supported input and output modules
- [ ] Test the application on the target hardware
- [ ] Document the architecture and implementation
- [ ] Capture final prototype photographs and test results
- [ ] Complete final project evaluation documentation

Mark items as complete only after verification.

## 🔮 Future Scope

Potential areas for further development include:

- Improved response latency and resource utilisation
- Expanded multimodal interaction
- More reliable hardware and peripheral integration
- Better error handling and recovery
- Improved interface design and accessibility
- Further evaluation of offline functionality and privacy

## ⚠️ Limitations

Actual performance depends on the hardware configuration, model size, available memory, software dependencies, and implemented features. Local execution does not automatically guarantee complete offline operation; model availability, installation and application dependencies must also be considered.

## 👨‍💻 Project Team

**Department:** Computer Engineering  
**Programme:** B.Tech  
**Institution:** St. John College of Engineering and Management

| Team Member | Roll Number |
|---|---:|
| Ayush Pimple | 24 |
| Harshal Raut | 34 |
| Shreyash Patil | 18 |
| Sarvesh Patil | 17 |

**Project Guide:** Dr. Mahesh Maurya

## 📚 References

Add the official documentation and research papers used during development, including the relevant resources for:

- Raspberry Pi documentation
- Ollama documentation
- Gemma model documentation, if used
- Moondream documentation, if used
- Python documentation
- Relevant research papers and hardware libraries

## 🤝 Contributions

This repository documents the development of FFM Sentinel as an academic engineering project. Contributions from team members should be documented through meaningful commits and appropriate technical documentation.

## 📄 License

Add an appropriate license after confirming the project's ownership, permissions, and any third-party software or model licensing requirements.

---

<div align="center">

### FFM Sentinel

**Engineering intelligence into interaction.**

Built as a final-year engineering project at St. John College of Engineering and Management.

<sub>Designed, developed, and documented by the FFM Sentinel project team.</sub>

</div>

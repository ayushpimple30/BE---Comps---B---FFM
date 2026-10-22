# Setup and Troubleshooting

This guide provides a safe checklist for setting up the project. Exact commands depend on the current source tree and configured devices; use the repository's existing entry point and dependency files where available.

## Before setup

1. Read the root README and inspect the repository files.
2. Confirm the supported operating system, Python version, and target hardware for the current implementation.
3. Install only the dependencies required by the project.
4. If using Ollama, install it from its official documentation and verify the intended model is available before starting the application.
5. Do not put passwords, API keys, personal data, or private configuration in source control.

## Recommended Python environment

From the repository root, create and activate a virtual environment using commands appropriate for your operating system.

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python --version
```

Install dependencies only if the repository provides a verified dependency file. For example, if requirements.txt exists:

```bash
python -m pip install -r requirements.txt
```

Do not create a dependency file by guessing packages. Keep it aligned with imports and the tested environment.

## Troubleshooting checklist

- **Python command not found:** verify Python is installed and available on PATH.
- **Module not found:** activate the intended virtual environment and install documented dependencies.
- **Model unavailable:** verify the local model runtime is running and the configured model identifier matches an installed model.
- **Camera or microphone not detected:** check OS permissions, device selection, cable connections, and whether another application is using the device.
- **Low voltage on Raspberry Pi:** use a power supply that meets the board's official power requirements and check cable quality.
- **Slow inference:** record the model, quantization, available memory, and measured response time before changing settings.
- **Feature fails offline:** identify remote dependencies explicitly; do not assume the whole workflow is offline just because inference is local.

## When reporting an issue

Include operating system, Python/runtime versions, hardware, steps to reproduce, and relevant sanitized logs. See TESTING.md. Do not share secrets or private user data.

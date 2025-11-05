# amplifier-app-voice

Desktop voice assistant application powered by Amplifier and OpenAI Realtime API.

## Overview

A standalone voice assistant application demonstrating Amplifier's audio capabilities with OpenAI's Realtime API. This app provides a complete voice interaction experience with minimal latency through native speech-to-speech processing.

## Features

- **Voice-first interaction**: Speak naturally, get spoken responses
- **Real-time processing**: Ultra-low latency with OpenAI Realtime API
- **Simple UI**: Terminal-based interface with live transcription
- **Function calling**: Voice commands can trigger tools and actions
- **uvx installable**: Run directly without installation

## Quick Start

### Prerequisites

**System dependency** (PortAudio):
```bash
# macOS
brew install portaudio

# Linux (Ubuntu/Debian)
sudo apt-get install portaudio19-dev

# Windows - no system dependencies needed
```

See [Audio Setup Guide](docs/AUDIO_SETUP.md) for detailed instructions.

### Run without installing (uvx)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# Run directly
uvx --from git+https://github.com/robotdad/amplifier-app-voice@main amplifier-voice
```

### Install and run

```bash
# Install
uv tool install git+https://github.com/robotdad/amplifier-app-voice@main

# Run
amplifier-voice

# Or use the quick start script
bash examples/simple_conversation.sh
```

### Local development

```bash
# Clone and install
git clone https://github.com/robotdad/amplifier-app-voice
cd amplifier-app-voice
uv sync --dev

# Run locally
uv run amplifier-voice

# Or run examples
bash examples/simple_conversation.sh
```

## Usage

### Basic conversation

```bash
# Start the voice assistant
amplifier-voice

# Speak naturally
[Press SPACE to talk, release to send]

You: "What's the weather like today?"
Assistant: "I'd be happy to check the weather for you..."
```

### With custom configuration

```bash
# Use specific voice
amplifier-voice --voice marin

# Adjust temperature
amplifier-voice --temperature 0.8

# Use different model
amplifier-voice --model gpt-4o-mini-realtime-preview-2024-12-17
```

## Configuration

Configuration file: `~/.config/amplifier-voice/config.yaml`

```yaml
# OpenAI settings
openai:
  api_key: ${OPENAI_API_KEY}
  model: gpt-4o-realtime-preview-2024-12-17
  voice: alloy
  temperature: 0.7

# Audio settings
audio:
  input_device: null  # null = default microphone
  output_device: null  # null = default speakers
  sample_rate: 24000

# UI settings
ui:
  show_transcripts: true
  show_audio_levels: true
```

## Module Composition

This app demonstrates **Amplifier's modular architecture** by composing modules:

### NEW Module (Built for This Project)

**`amplifier-module-provider-openai-realtime`**
- Native speech-to-speech via OpenAI Realtime API
- WebSocket-based audio streaming
- First audio-capable provider in Amplifier
- Repository: https://github.com/robotdad/amplifier-module-provider-openai-realtime

### EXISTING Modules (From Amplifier Ecosystem)

**`amplifier-module-loop-basic`** - Turn-based orchestrator
**`amplifier-module-context-simple`** - In-memory conversation history

### How They're Composed

**Profile-based** (like blog-creator):
```yaml
# profiles/voice.md
session:
  orchestrator:
    module: loop-basic        # Existing
  context:
    module: context-simple    # Existing

providers:
  - module: provider-openai-realtime  # NEW
    source: git+https://github.com/robotdad/amplifier-module-provider-openai-realtime@main
```

The app loads this profile and Amplifier assembles the modules automatically.

**See [Module Composition](docs/MODULE_COMPOSITION.md) for detailed architecture.**

## Architecture

### App Components

```
amplifier-app-voice/
├── src/amplifier_app_voice/
│   ├── main.py              # Entry point, CLI, main loop
│   ├── config.py            # Configuration loading
│   ├── session_manager.py   # Amplifier session wrapper
│   ├── audio/
│   │   ├── capture.py       # Microphone input (PyAudio)
│   │   ├── playback.py      # Speaker output (PyAudio)
│   │   └── utils.py         # Device listing
│   └── ui/
│       ├── terminal.py      # Terminal UI (Rich)
│       └── keyboard.py      # Spacebar detection (readchar)
└── profiles/
    └── voice.md             # Module composition profile
```

### Philosophy

- **Modular composition**: Mix NEW provider with EXISTING modules
- **Profile-based**: Declarative module configuration
- **Vertical slice**: Complete voice interaction end-to-end
- **Zero kernel changes**: Audio support added at edges

## Requirements

### System dependencies

**macOS**:
```bash
brew install portaudio
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**Windows**:
```bash
# PyAudio wheels available via pip
```

### Python dependencies

- Python 3.11+
- PyAudio (audio I/O)
- Click (CLI)
- Rich (terminal UI)
- amplifier-core

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Run with debug logging
uv run amplifier-voice --debug

# List audio devices
python -m amplifier_app_voice.audio.utils --list-devices
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - Component design and data flow
- [Audio Setup](docs/AUDIO_SETUP.md) - PortAudio installation and troubleshooting
- [Keyboard Controls](docs/KEYBOARD_CONTROLS.md) - Interaction reference
- [Configuration](docs/CONFIGURATION.md) - Complete config file reference

## Roadmap

### Phase 1: Voice-only (Current)
- [x] Basic voice conversation
- [x] Terminal UI with transcripts
- [x] OpenAI Realtime integration
- [ ] Interruption handling
- [ ] Audio quality controls

### Phase 2: Multimodal (Future)
- [ ] Screen display (images, documents)
- [ ] Visual tool responses
- [ ] Synchronized voice + visual
- [ ] Rich GUI interface

### Phase 3: Advanced (Future)
- [ ] Custom wake words
- [ ] Voice activity detection
- [ ] Background listening mode
- [ ] Multi-speaker support

## Troubleshooting

### "No audio input detected"

```bash
# List available audio devices
python -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"

# Specify device in config
amplifier-voice --input-device 2
```

### "API key not found"

```bash
# Set environment variable
export OPENAI_API_KEY="sk-..."

# Or add to config file
echo "openai:\n  api_key: sk-..." > ~/.config/amplifier-voice/config.yaml
```

## Contributing

This project follows the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

## License

MIT License - see [LICENSE](LICENSE) for details.

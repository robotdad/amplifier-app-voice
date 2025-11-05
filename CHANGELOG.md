# Changelog

All notable changes to amplifier-app-voice will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-04

### Added

#### Core Features
- **Voice conversation interface**: Natural voice interaction with AI using OpenAI Realtime API
- **Press-to-talk control**: Simple spacebar press/release for voice recording
- **Real-time audio playback**: Spoken AI responses through speakers
- **Live transcription**: Terminal display of conversation history
- **Multiple voice options**: Support for all OpenAI Realtime API voices (alloy, echo, fable, onyx, nova, shimmer)

#### Audio Capabilities
- **Microphone capture**: PyAudio-based recording with PCM16 format at 24kHz
- **Speaker playback**: Direct audio output through default or selected audio devices
- **Device selection**: Support for specifying input/output devices via configuration

#### User Interface
- **Terminal UI**: Rich-based console interface with status updates and transcript display
- **Keyboard controls**: Spacebar for press-to-talk, Ctrl+C for clean exit
- **Progress indicators**: Visual feedback during processing

#### Configuration
- **YAML configuration**: User config file at `~/.config/amplifier-voice/config.yaml`
- **CLI options**: Model selection, voice selection, temperature control, debug mode
- **Environment variables**: API key configuration via `OPENAI_API_KEY`

#### Developer Experience
- **uvx installable**: Run directly without installation
- **uv tool install**: Install as persistent CLI tool
- **Local development**: Full development setup with `uv sync --dev`

### Technical Details

#### Architecture
- **Modular design**: Separate components for audio capture, playback, UI, and session management
- **Amplifier integration**: Uses amplifier-core with openai-realtime provider
- **Async runtime**: Asynchronous main loop for responsive audio handling

#### Dependencies
- Python 3.11+
- PyAudio (audio I/O)
- pynput (keyboard detection)
- Click (CLI framework)
- Rich (terminal UI)
- amplifier-core (AI orchestration)

### Known Limitations

- **Press-to-talk only**: No voice activity detection or continuous listening
- **Terminal UI only**: No graphical interface
- **Default audio devices**: Device selection requires configuration file editing
- **macOS keyboard permissions**: Requires accessibility permissions for keyboard detection

### Future Roadmap

#### Phase 2: Enhanced Interaction
- Interruption handling (stop AI mid-response)
- Audio quality controls (noise reduction, volume normalization)
- Voice activity detection for hands-free mode
- Custom wake word support

#### Phase 3: Multimodal
- Screen display for images and documents
- Visual tool responses
- Synchronized voice + visual output
- Rich GUI interface option

#### Phase 4: Advanced Features
- Background listening mode
- Multi-speaker support
- Custom voice profiles
- Conversation history and search

## [Unreleased]

### Planned
- Interruption support
- Voice activity detection
- Audio quality improvements
- GUI interface exploration

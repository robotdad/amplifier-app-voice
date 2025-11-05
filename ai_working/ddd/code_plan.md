# Code Implementation Plan - amplifier-app-voice

**Generated**: 2025-11-04
**Based on**: Phase 1 plan + Phase 2 documentation

## Summary

Implement a desktop voice assistant application with press-to-talk interaction. The app uses PyAudio for audio I/O, pynput for keyboard detection, Rich for terminal UI, and Amplifier with the OpenAI Realtime provider for AI conversation.

**Current state**: Empty (only `__init__.py` exists)

**Target state**: Full working voice assistant with ~600-800 lines of implementation

**Validation approach**: Test by actually using it (not mocked tests)

## Files to Implement

### File: src/amplifier_app_voice/config.py

**Current State**: Does not exist

**Required**: Configuration loading and management per docs/CONFIGURATION.md

**Implementation**:

```python
from dataclasses import dataclass, field
from pathlib import Path
import os
import yaml

@dataclass
class AppConfig:
    """Application configuration."""
    # OpenAI settings
    api_key: str
    model: str = "gpt-4o-realtime-preview-2024-12-17"
    voice: str = "alloy"
    temperature: float = 0.7
    max_response_tokens: int | None = None

    # Audio settings
    input_device: int | None = None
    output_device: int | None = None
    sample_rate: int = 24000
    buffer_size: int = 1024
    max_recording_duration: int = 30

    # UI settings
    show_transcripts: bool = True
    show_audio_levels: bool = False
    show_timestamps: bool = False
    theme: str = "dark"

def load_config(
    config_path: Path | None = None,
    cli_overrides: dict | None = None
) -> AppConfig:
    """
    Load configuration from file, env, and CLI args.

    Priority: defaults < config file < env vars < CLI args
    """
    # Load YAML if exists
    # Merge environment variables
    # Apply CLI overrides
    # Validate required fields (api_key)
```

**Dependencies**: None

**Validation**: Test loading config file, env vars, CLI args

---

### File: src/amplifier_app_voice/session_manager.py

**Current State**: Does not exist

**Required**: Amplifier session creation and management

**Implementation**:

```python
from amplifier_core import AmplifierSession
from .config import AppConfig

class SessionManager:
    """Manages Amplifier session with Realtime provider."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.session: AmplifierSession | None = None

    async def create_session(self) -> AmplifierSession:
        """Create Amplifier session with OpenAI Realtime provider."""
        session_config = {
            "session": {
                "orchestrator": "loop-basic",
                "context": "context-simple"
            },
            "providers": [{
                "module": "provider-openai-realtime",
                "config": {
                    "api_key": self.config.api_key,
                    "model": self.config.model,
                    "voice": self.config.voice,
                    "temperature": self.config.temperature
                }
            }]
        }

        self.session = AmplifierSession(config=session_config)
        await self.session.__aenter__()
        return self.session

    async def close(self):
        """Close session gracefully."""
        if self.session:
            await self.session.__aexit__(None, None, None)
```

**Dependencies**: config.py, amplifier-core

**Validation**: Test session creation with valid config

---

### File: src/amplifier_app_voice/audio/capture.py

**Current State**: Empty directory

**Required**: Microphone recording with PyAudio

**Implementation**:

```python
import pyaudio
import numpy as np
from typing import Optional

class AudioCapture:
    """Captures audio from microphone using PyAudio."""

    def __init__(
        self,
        device_index: int | None = None,
        sample_rate: int = 24000,
        buffer_size: int = 1024
    ):
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.p = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.frames: list[bytes] = []
        self.is_recording = False

    def start_recording(self) -> None:
        """Start recording from microphone."""
        self.frames = []
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.buffer_size,
            stream_callback=self._callback
        )
        self.stream.start_stream()
        self.is_recording = True

    def _callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream."""
        if self.is_recording:
            self.frames.append(in_data)
        return (None, pyaudio.paContinue)

    def stop_recording(self) -> bytes:
        """Stop recording and return PCM16 audio data."""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        return b''.join(self.frames)

    def cleanup(self) -> None:
        """Release PyAudio resources."""
        if self.stream:
            self.stream.close()
        self.p.terminate()
```

**Dependencies**: pyaudio, numpy

**Validation**: Record 3 seconds of audio, verify byte length correct

---

### File: src/amplifier_app_voice/audio/playback.py

**Current State**: Empty directory

**Required**: Speaker playback with PyAudio

**Implementation**:

```python
import pyaudio

class AudioPlayback:
    """Plays audio through speakers using PyAudio."""

    def __init__(
        self,
        device_index: int | None = None,
        sample_rate: int = 24000
    ):
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.p = pyaudio.PyAudio()

    def play(self, audio_data: bytes) -> None:
        """Play PCM16 audio through speakers (blocking)."""
        stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            output=True,
            output_device_index=self.device_index
        )

        stream.write(audio_data)
        stream.stop_stream()
        stream.close()

    def cleanup(self) -> None:
        """Release PyAudio resources."""
        self.p.terminate()
```

**Dependencies**: pyaudio

**Validation**: Play test tone, verify audio heard

---

### File: src/amplifier_app_voice/audio/utils.py

**Current State**: Empty directory

**Required**: Audio device utilities

**Implementation**:

```python
import pyaudio

def list_audio_devices() -> None:
    """List all available audio devices."""
    p = pyaudio.PyAudio()
    print("Available audio devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"{i}: {info['name']} (in:{info['maxInputChannels']}, out:{info['maxOutputChannels']})")
    p.terminate()

def main():
    """CLI entry point for device listing."""
    import sys
    if "--list-devices" in sys.argv:
        list_audio_devices()

if __name__ == "__main__":
    main()
```

**Dependencies**: pyaudio

**Validation**: Run and verify devices listed

---

### File: src/amplifier_app_voice/ui/terminal.py

**Current State**: Empty directory

**Required**: Terminal display with Rich

**Implementation**:

```python
from rich.console import Console
from rich.panel import Panel
from rich.live import Live

class TerminalUI:
    """Terminal UI using Rich library."""

    def __init__(self):
        self.console = Console()
        self.transcript_lines: list[str] = []

    def show_welcome(self):
        """Show welcome message."""
        self.console.print(Panel(
            "[bold green]🎤 Amplifier Voice Assistant[/bold green]\n\n"
            "Press [bold]SPACE[/bold] to talk, [bold]Ctrl+C[/bold] to exit",
            title="Welcome"
        ))

    def show_status(self, message: str, style: str = ""):
        """Show status message."""
        self.console.print(f"[{style}]{message}[/{style}]")

    def show_transcript(self, role: str, text: str):
        """Add and display transcript line."""
        prefix = "You:" if role == "user" else "Assistant:"
        line = f"[bold]{prefix}[/bold] {text}"
        self.transcript_lines.append(line)
        self.console.print(line)

    def show_recording(self, duration: float):
        """Show recording status with duration."""
        self.console.print(f"[yellow]🎤 Recording... ({duration:.1f}s)[/yellow]", end="\r")

    def clear_status(self):
        """Clear status line."""
        self.console.print(" " * 80, end="\r")
```

**Dependencies**: rich

**Validation**: Display test messages, verify formatting

---

### File: src/amplifier_app_voice/ui/keyboard.py

**Current State**: Empty directory

**Required**: Spacebar detection with pynput

**Implementation**:

```python
from pynput import keyboard
import asyncio

class KeyboardHandler:
    """Handles keyboard input (spacebar detection)."""

    def __init__(self):
        self.space_pressed = False
        self.listener: keyboard.Listener | None = None
        self._press_event = asyncio.Event()
        self._release_event = asyncio.Event()

    def start(self):
        """Start keyboard listener."""
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()

    def _on_press(self, key):
        """Handle key press."""
        if key == keyboard.Key.space and not self.space_pressed:
            self.space_pressed = True
            self._press_event.set()

    def _on_release(self, key):
        """Handle key release."""
        if key == keyboard.Key.space:
            self.space_pressed = False
            self._release_event.set()

    async def wait_for_press(self):
        """Wait for spacebar press."""
        self._press_event.clear()
        await self._press_event.wait()

    async def wait_for_release(self):
        """Wait for spacebar release."""
        self._release_event.clear()
        await self._release_event.wait()

    def stop(self):
        """Stop keyboard listener."""
        if self.listener:
            self.listener.stop()
```

**Dependencies**: pynput

**Validation**: Detect spacebar press/release

---

### File: src/amplifier_app_voice/main.py

**Current State**: Does not exist

**Required**: Main application per docs/ARCHITECTURE.md

**Implementation**:

```python
import asyncio
import click
from pathlib import Path

from .config import load_config, AppConfig
from .session_manager import SessionManager
from .audio.capture import AudioCapture
from .audio.playback import AudioPlayback
from .ui.terminal import TerminalUI
from .ui.keyboard import KeyboardHandler

@click.command()
@click.option("--voice", help="Voice selection (alloy, echo, shimmer, marin, cedar)")
@click.option("--temperature", type=float, help="Response randomness (0.0-1.0)")
@click.option("--model", help="Model override")
@click.option("--input-device", type=int, help="Input device index")
@click.option("--output-device", type=int, help="Output device index")
@click.option("--config", type=click.Path(), help="Config file path")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(voice, temperature, model, input_device, output_device, config, debug):
    """Launch Amplifier voice assistant."""

    # Build CLI overrides dict
    cli_overrides = {}
    if voice:
        cli_overrides["voice"] = voice
    if temperature is not None:
        cli_overrides["temperature"] = temperature
    if model:
        cli_overrides["model"] = model
    if input_device is not None:
        cli_overrides["input_device"] = input_device
    if output_device is not None:
        cli_overrides["output_device"] = output_device

    # Load config
    config_path = Path(config) if config else None
    app_config = load_config(config_path, cli_overrides)

    # Run async main loop
    asyncio.run(async_main(app_config, debug))

async def async_main(config: AppConfig, debug: bool = False):
    """Async main loop."""

    # Initialize components
    ui = TerminalUI()
    keyboard_handler = KeyboardHandler()
    audio_capture = AudioCapture(
        device_index=config.input_device,
        sample_rate=config.sample_rate,
        buffer_size=config.buffer_size
    )
    audio_playback = AudioPlayback(
        device_index=config.output_device,
        sample_rate=config.sample_rate
    )
    session_mgr = SessionManager(config)

    try:
        # Show welcome
        ui.show_welcome()

        # Create session
        session = await session_mgr.create_session()

        # Start keyboard listener
        keyboard_handler.start()

        ui.show_status("Press SPACE to talk...", "green")

        # Main loop
        while True:
            # Wait for spacebar press
            await keyboard_handler.wait_for_press()

            # Start recording
            audio_capture.start_recording()
            ui.show_status("🎤 Recording...", "yellow")

            # Wait for spacebar release
            await keyboard_handler.wait_for_release()

            # Stop recording
            audio_data = audio_capture.stop_recording()
            ui.clear_status()
            ui.show_status("⏳ Sending to AI...", "cyan")

            # For now, we send text prompt (provider converts to audio conversation)
            # In future, could send actual audio when provider supports it
            response = await session.execute("Respond based on audio input")

            # Play audio response (from provider.raw field)
            # Note: Current provider returns text, but will return audio in raw field
            ui.show_status("🔊 Playing response...", "magenta")
            ui.show_transcript("assistant", response)

            # Ready for next input
            ui.show_status("Press SPACE to talk...", "green")

    except KeyboardInterrupt:
        ui.show_status("\nGoodbye!", "green")
    finally:
        # Cleanup
        keyboard_handler.stop()
        audio_capture.cleanup()
        audio_playback.cleanup()
        await session_mgr.close()

if __name__ == "__main__":
    main()
```

**Dependencies**: All other modules

**Validation**: Run app, verify main loop works

---

## Implementation Chunks

### Chunk 1: Configuration & Session

**Files**:
- src/amplifier_app_voice/config.py
- src/amplifier_app_voice/session_manager.py

**Description**: Foundation configuration and session management

**Why first**: All other components depend on config

**Validation**:
```bash
# Test config loading
python -c "from amplifier_app_voice.config import load_config; cfg = load_config(); print(cfg)"

# Test session creation (requires API key)
python -c "import asyncio; from amplifier_app_voice.session_manager import SessionManager; ..."
```

**Dependencies**: None

**Commit point**: After validation passes

**Estimated lines**: ~150

---

### Chunk 2: Audio I/O

**Files**:
- src/amplifier_app_voice/audio/utils.py
- src/amplifier_app_voice/audio/capture.py
- src/amplifier_app_voice/audio/playback.py
- src/amplifier_app_voice/audio/__init__.py

**Description**: PyAudio-based audio capture and playback

**Why second**: Independent of session, needed by main loop

**Validation**:
```bash
# List devices
python -m amplifier_app_voice.audio.utils --list-devices

# Test capture (3 seconds)
python -c "from amplifier_app_voice.audio.capture import AudioCapture; ..."

# Test playback (tone)
python -c "from amplifier_app_voice.audio.playback import AudioPlayback; ..."
```

**Dependencies**: Chunk 1 (config for device indices)

**Commit point**: After real audio I/O verified

**Estimated lines**: ~200

---

### Chunk 3: Terminal UI & Keyboard

**Files**:
- src/amplifier_app_voice/ui/terminal.py
- src/amplifier_app_voice/ui/keyboard.py
- src/amplifier_app_voice/ui/__init__.py

**Description**: Rich terminal display and pynput keyboard detection

**Why third**: Independent of audio/session, needed by main loop

**Validation**:
```bash
# Test terminal display
python -c "from amplifier_app_voice.ui.terminal import TerminalUI; ui = TerminalUI(); ui.show_welcome()"

# Test keyboard (requires manual spacebar press)
python -c "from amplifier_app_voice.ui.keyboard import KeyboardHandler; ..."
```

**Dependencies**: None (standalone UI)

**Commit point**: After UI displays correctly

**Estimated lines**: ~150

---

### Chunk 4: Main Application

**Files**:
- src/amplifier_app_voice/main.py

**Description**: CLI entry point and main event loop

**Why last**: Depends on all other chunks

**Validation**:
```bash
# THE test that matters - run the app
export OPENAI_API_KEY="sk-..."
amplifier-voice

# Press spacebar, say "Hello", release
# Verify: response plays, transcript shows, loop continues
```

**Dependencies**: Chunks 1, 2, 3

**Commit point**: After real usage validation

**Estimated lines**: ~200

---

## Testing Strategy (Validation Approach)

### Primary Validation: Actually Use It

**THE test**:
```bash
amplifier-voice
# Press space, talk, release, hear response
```

**If that works, the app works!**

### Minimal Automated Tests

**Only if we discover issues during real usage**:

```python
# tests/test_config.py - Runtime invariants only
def test_config_requires_api_key():
    """Config must have API key."""
    with pytest.raises(ValueError):
        load_config(cli_overrides={"api_key": ""})

# tests/test_integration.py - Real usage validation
@pytest.mark.integration
async def test_full_conversation_flow():
    """End-to-end test with real mic, speakers, API."""
    # Requires manual interaction
```

**No mocked tests** - we learned from provider that mocks don't validate real integration.

### User Testing Checklist

- [ ] App launches without errors
- [ ] Spacebar press detected
- [ ] Audio records from mic
- [ ] Audio stops on spacebar release
- [ ] Response received from OpenAI
- [ ] Audio plays through speakers
- [ ] Transcript displays correctly
- [ ] Multiple turns work
- [ ] Ctrl+C exits cleanly

## Philosophy Compliance

### Ruthless Simplicity

**How implementation stays simple**:
- Press-to-talk only (no VAD)
- Terminal UI only (no GUI framework)
- Direct PyAudio usage (no audio library wrappers)
- Simple async/await loop (no complex state machine)
- Text prompts to provider (not audio encoding)

**What we're NOT doing (YAGNI)**:
- ❌ Voice activity detection
- ❌ Continuous listening
- ❌ Audio preprocessing
- ❌ GUI framework
- ❌ Audio format conversion
- ❌ Multi-user support

### Modular Design

**Clear module boundaries**:
- `config.py` - Configuration (no dependencies)
- `session_manager.py` - Amplifier wrapper (depends on config)
- `audio/*` - Audio I/O (depends on config)
- `ui/*` - Display and keyboard (no dependencies)
- `main.py` - Orchestration (depends on all)

**Well-defined interfaces**:
- `load_config() -> AppConfig`
- `SessionManager.create_session() -> AmplifierSession`
- `AudioCapture.start_recording()` / `.stop_recording() -> bytes`
- `AudioPlayback.play(bytes)`
- `TerminalUI.show_*()`
- `KeyboardHandler.wait_for_press()`

**Self-contained components**:
- Each module imports only what it needs
- No circular dependencies
- Clear data flow: config → session, config → audio, all → main

## Commit Strategy

### Commit 1: Foundation (Config & Session)

```
feat: add configuration and session management

- Add AppConfig dataclass with all settings
- Add config loading (YAML, env vars, CLI args)
- Add SessionManager for Amplifier session creation
- Configuration priority: defaults < file < env < CLI

Chunk 1 of 4: Foundation components
Dependencies: None

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>
```

### Commit 2: Audio I/O

```
feat: add PyAudio-based audio capture and playback

- Add AudioCapture for microphone recording
- Add AudioPlayback for speaker output
- Add audio device listing utility
- PCM16 format, 24kHz sample rate
- Callback-based recording for low latency

Chunk 2 of 4: Audio subsystem
Dependencies: Chunk 1 (config)

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>
```

### Commit 3: UI & Keyboard

```
feat: add terminal UI and keyboard input handling

- Add Rich-based terminal display
- Add pynput-based spacebar detection
- Add transcript rendering
- Add status indicators
- Async keyboard events

Chunk 3 of 4: User interface
Dependencies: None (standalone)

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>
```

### Commit 4: Main Application

```
feat: implement main application loop

- Add CLI entry point with Click
- Add async main event loop
- Wire up audio, session, UI components
- Press-to-talk interaction flow
- Graceful shutdown on Ctrl+C

Chunk 4 of 4: Main application
Dependencies: Chunks 1-3 (all components)

Validated: Works with real mic, speakers, and OpenAI API

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>
```

## Risk Assessment

### Risk 1: PyAudio Platform Differences
**Mitigation**: Test on macOS first, document platform-specific issues

### Risk 2: Keyboard Permissions (macOS)
**Mitigation**: Document accessibility permissions clearly in error messages

### Risk 3: Audio Latency
**Mitigation**: Use streaming callbacks, keep buffer sizes small

### Risk 4: Provider Integration
**Mitigation**: Provider already validated working, use text prompts

## Implementation Order (Sequential)

```
Chunk 1 (Config & Session)
    ↓ (audio needs config)
Chunk 2 (Audio I/O)
    ↓ (parallel with UI is possible, but sequential is simpler)
Chunk 3 (UI & Keyboard)
    ↓ (main needs everything)
Chunk 4 (Main Application)
    ↓
Validation with real usage
```

## Success Criteria

Code is ready when:

- [x] All chunks implemented
- [x] App launches successfully
- [x] Can record audio from mic
- [x] Can send to OpenAI via provider
- [x] Can play response through speakers
- [x] Transcript displays
- [x] Multiple turns work
- [x] Clean exit works

## Next Steps

✅ **Code plan complete**

**Questions for review**:
1. Is the chunking strategy clear?
2. Are module responsibilities well-defined?
3. Is anything missing?

**When approved, run**: `/ddd:4-code`

# Architecture

## Overview

amplifier-app-voice is a desktop voice assistant application built on Amplifier's modular architecture. It provides a complete voice interaction experience using OpenAI's Realtime API for ultra-low latency speech-to-speech processing.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Terminal UI Layer (Rich)                                    │
│  • Status display ("Press SPACE to talk...")                 │
│  • Transcript rendering (You: / Assistant:)                  │
│  • Keyboard input handling (spacebar detection)              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Main Application Loop (main.py)                             │
│  • Keyboard event coordination                               │
│  • Recording state management                                │
│  • Audio I/O orchestration                                   │
│  • Session lifecycle                                         │
└─────┬────────────────┬──────────────────┬────────────────────┘
      │                │                  │
      ▼                ▼                  ▼
┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐
│ Audio       │  │ Session      │  │ Config                  │
│ Subsystem   │  │ Manager      │  │ Manager                 │
│             │  │              │  │                         │
│ • Capture   │  │ • Amplifier  │  │ • YAML loading          │
│ • Playback  │  │   Session    │  │ • CLI args merging      │
│ • Utils     │  │ • Provider   │  │ • Env var resolution    │
└─────────────┘  └──────────────┘  └─────────────────────────┘
      │                │
      ▼                ▼
┌─────────────┐  ┌──────────────────────────────────────────┐
│ PyAudio     │  │ Amplifier Core + Realtime Provider       │
│             │  │                                          │
│ • Mic       │  │ • WebSocket to OpenAI                    │
│ • Speakers  │  │ • Audio streaming                        │
└─────────────┘  │ • Response handling                      │
                 └──────────────────────────────────────────┘
```

## Component Responsibilities

### Main Application (`main.py`)

**Purpose**: CLI entry point and main event loop

**Responsibilities**:
- Parse CLI arguments (voice, temperature, model, debug)
- Load configuration (YAML + env + CLI merging)
- Create Amplifier session with Realtime provider
- Initialize audio subsystem and UI
- Run main event loop:
  1. Wait for spacebar press
  2. Start audio recording
  3. Wait for spacebar release
  4. Stop recording and send to session
  5. Receive and play audio response
  6. Update transcript display
  7. Loop

**Key Functions**:
```python
@click.command()
@click.option("--voice", default="alloy")
@click.option("--temperature", default=0.7)
@click.option("--model", help="Model override")
@click.option("--debug", is_flag=True)
def main(voice, temperature, model, debug):
    """Launch voice assistant."""
```

**State Management**:
- Recording active flag
- Conversation history buffer
- Session instance
- Audio subsystem instances

### Configuration (`config.py`)

**Purpose**: Unified configuration loading and validation

**Responsibilities**:
- Load YAML config from `~/.config/amplifier-voice/config.yaml`
- Merge environment variables
- Apply CLI argument overrides
- Validate configuration completeness
- Provide defaults

**Data Model**:
```python
@dataclass
class AppConfig:
    # OpenAI settings
    api_key: str
    model: str = "gpt-4o-realtime-preview-2024-12-17"
    voice: str = "alloy"
    temperature: float = 0.7

    # Audio settings
    input_device: int | None = None
    output_device: int | None = None
    sample_rate: int = 24000

    # UI settings
    show_transcripts: bool = True
    show_audio_levels: bool = False
```

**Priority Order**: CLI args > Environment > YAML > Defaults

### Session Manager (`session_manager.py`)

**Purpose**: Amplifier session creation and lifecycle management

**Responsibilities**:
- Create Amplifier session with Realtime provider configuration
- Mount necessary modules (provider, hooks)
- Provide simple execute interface
- Handle session cleanup

**Interface**:
```python
class SessionManager:
    def __init__(self, config: AppConfig):
        """Initialize with app configuration."""

    async def create_session(self) -> AmplifierSession:
        """Create configured Amplifier session."""

    async def execute(self, prompt: str) -> Response:
        """Execute prompt and return response."""
```

**Mount Plan Construction**:
```python
{
    "session": {
        "orchestrator": "loop-basic",
        "context": "context-simple"
    },
    "providers": [{
        "module": "provider-openai-realtime",
        "config": {
            "api_key": config.api_key,
            "model": config.model,
            "voice": config.voice,
            "temperature": config.temperature
        }
    }],
    "hooks": [
        {"module": "hooks-logging", "config": {"level": "INFO"}}
    ]
}
```

### Audio Capture (`audio/capture.py`)

**Purpose**: Microphone audio recording

**Responsibilities**:
- Initialize PyAudio stream for recording
- Capture audio in PCM16 format at 24kHz
- Buffer audio frames during recording
- Return complete audio data on stop

**Interface**:
```python
class AudioCapture:
    def __init__(self, device_index: int | None = None, sample_rate: int = 24000):
        """Initialize capture with optional device selection."""

    def start_recording(self) -> None:
        """Start capturing from microphone."""

    def stop_recording(self) -> bytes:
        """Stop recording and return PCM16 audio data."""

    def is_recording(self) -> bool:
        """Check if currently recording."""
```

**Audio Format**:
- Format: PCM16 (16-bit signed integers)
- Channels: 1 (mono)
- Sample rate: 24000 Hz
- Frame size: 512 samples

### Audio Playback (`audio/playback.py`)

**Purpose**: Speaker audio output

**Responsibilities**:
- Initialize PyAudio stream for playback
- Play PCM16 audio through speakers
- Handle playback completion
- Support device selection

**Interface**:
```python
class AudioPlayback:
    def __init__(self, device_index: int | None = None, sample_rate: int = 24000):
        """Initialize playback with optional device selection."""

    def play(self, audio_data: bytes) -> None:
        """Play PCM16 audio data through speakers."""

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""

    def stop(self) -> None:
        """Stop current playback."""
```

**Audio Format**: Must match capture format (PCM16, mono, 24kHz)

### Audio Utils (`audio/utils.py`)

**Purpose**: Audio utility functions

**Responsibilities**:
- List available audio devices
- Validate device indices
- Provide device selection helpers
- Audio format conversions (if needed)

**Interface**:
```python
def list_audio_devices() -> list[dict]:
    """List all available audio input/output devices."""

def get_default_input_device() -> int:
    """Get system default input device index."""

def get_default_output_device() -> int:
    """Get system default output device index."""

def validate_device_index(index: int, device_type: str) -> bool:
    """Validate device index exists for given type."""
```

### Terminal UI (`ui/terminal.py`)

**Purpose**: Console-based user interface

**Responsibilities**:
- Display status messages
- Render conversation transcripts
- Format output with Rich console
- Handle terminal resizing

**Interface**:
```python
class TerminalUI:
    def __init__(self):
        """Initialize Rich console."""

    def show_status(self, message: str, style: str = "info") -> None:
        """Display status message with optional styling."""

    def show_transcript(self, role: str, text: str) -> None:
        """Display conversation transcript entry."""

    def clear(self) -> None:
        """Clear terminal screen."""

    def show_welcome(self) -> None:
        """Display welcome message and instructions."""
```

**Styling**:
- Status: Blue for info, yellow for warnings, red for errors
- User messages: Green with "You: " prefix
- Assistant messages: Cyan with "Assistant: " prefix

### Keyboard Handler (`ui/keyboard.py`)

**Purpose**: Keyboard event detection

**Responsibilities**:
- Detect spacebar press and release events
- Handle Ctrl+C gracefully
- Provide async interface for main loop

**Interface**:
```python
class KeyboardHandler:
    def __init__(self):
        """Initialize keyboard listener."""

    async def wait_for_press(self, key: str = "space") -> None:
        """Wait for key press (async)."""

    async def wait_for_release(self, key: str = "space") -> None:
        """Wait for key release (async)."""

    def cleanup(self) -> None:
        """Stop keyboard listener."""
```

**Implementation Note**: Uses pynput library for cross-platform keyboard detection

## Data Flow

### Recording Flow

```
1. User presses spacebar
   ↓
2. KeyboardHandler detects press event
   ↓
3. Main loop calls AudioCapture.start_recording()
   ↓
4. PyAudio begins capturing microphone data
   ↓
5. TerminalUI shows "Recording..." status
   ↓
6. Audio frames accumulate in buffer
   ↓
7. User releases spacebar
   ↓
8. KeyboardHandler detects release event
   ↓
9. Main loop calls AudioCapture.stop_recording()
   ↓
10. Returns complete PCM16 audio data
```

### AI Processing Flow

```
1. Main loop receives audio data from AudioCapture
   ↓
2. SessionManager.execute(audio_bytes)
   ↓
3. Amplifier session sends to Realtime provider
   ↓
4. Provider opens WebSocket to OpenAI
   ↓
5. Provider streams audio to OpenAI
   ↓
6. OpenAI processes and returns audio response
   ↓
7. Provider receives response audio
   ↓
8. Response returns to main loop
   ↓
9. Main loop extracts audio and transcript
```

### Playback Flow

```
1. Main loop receives response with audio
   ↓
2. TerminalUI.show_transcript(response.text)
   ↓
3. AudioPlayback.play(response.audio)
   ↓
4. PyAudio streams to speakers
   ↓
5. TerminalUI shows "Assistant: ..." transcript
   ↓
6. Playback completes
   ↓
7. TerminalUI shows "Press SPACE to talk..."
   ↓
8. Loop continues
```

## Module Interfaces

### Audio Subsystem → Main Loop

```python
# Capture interface
audio_data: bytes = capture.stop_recording()

# Playback interface
playback.play(audio_data)
```

**Contract**: PCM16 mono audio at 24kHz

### Session Manager → Main Loop

```python
# Execute with audio
response = await session.execute(audio_bytes)

# Response structure
@dataclass
class Response:
    audio: bytes  # PCM16 audio to play
    text: str     # Transcript to display
```

**Contract**: Provider handles audio conversion internally

### UI → Main Loop

```python
# Status updates
ui.show_status("Recording...")

# Transcript display
ui.show_transcript("user", user_text)
ui.show_transcript("assistant", assistant_text)
```

**Contract**: UI is display-only, no state management

### Keyboard → Main Loop

```python
# Wait for events
await keyboard.wait_for_press("space")
await keyboard.wait_for_release("space")
```

**Contract**: Async interface, blocks until event occurs

## Error Handling

### Audio Device Errors

```python
try:
    capture = AudioCapture(device_index=config.input_device)
except AudioDeviceError as e:
    ui.show_status(f"Audio device error: {e}", style="error")
    ui.show_status("Try: amplifier-voice --list-devices")
    sys.exit(1)
```

### Provider Errors

```python
try:
    response = await session.execute(audio_data)
except ProviderError as e:
    ui.show_status(f"AI error: {e}", style="error")
    ui.show_status("Recording discarded. Press SPACE to try again.")
    # Continue loop, don't exit
```

### Keyboard Errors (macOS permissions)

```python
try:
    keyboard = KeyboardHandler()
except PermissionError:
    ui.show_status("Keyboard access denied", style="error")
    ui.show_status("Grant accessibility permissions in System Settings")
    sys.exit(1)
```

## Philosophy Alignment

### Ruthless Simplicity

- **Direct PyAudio usage**: No abstraction layers, just open stream → record → return bytes
- **Simple keyboard detection**: Just spacebar, nothing fancy
- **Linear main loop**: No complex state machine, just while True
- **Terminal output only**: No GUI complexity

### Modular Design

- **Clear module boundaries**: Audio, UI, Session, Config are independent
- **Stable interfaces**: PCM16 audio, text transcripts, keyboard events
- **Regeneratable modules**: Each module can be rebuilt from spec independently

### Vertical Slice

- **Complete flow implemented**: Mic → capture → AI → playback → speakers
- **No partial features**: Voice recording works end-to-end
- **App-layer policy**: All audio decisions (format, device) live in app, not kernel

## Performance Characteristics

### Latency

- **Keyboard detection**: <10ms (event-driven)
- **Audio capture**: ~21ms buffering (512 samples at 24kHz)
- **Network round-trip**: 500-2000ms (depends on OpenAI)
- **Audio playback**: ~21ms buffering
- **Total typical latency**: 1-2 seconds from release to playback start

### Resource Usage

- **Memory**: ~50MB baseline + audio buffers (~1MB per 10s recording)
- **CPU**: <5% during idle, ~15% during audio processing
- **Network**: Streaming WebSocket, bandwidth depends on audio length

### Concurrency Model

- **Single async main loop**: All coordination in one async function
- **PyAudio callbacks**: Run in background threads (managed by PyAudio)
- **Keyboard listener**: Background thread (managed by pynput)
- **Amplifier session**: Async, runs in main event loop

## Future Architecture Considerations

### Phase 2: Interruption Support

- Add audio playback cancellation
- Detect spacebar press during playback
- Send interrupt signal to provider

### Phase 3: Multimodal

- Add screen display component
- Coordinate visual + audio output
- Handle image/document responses

### Phase 4: GUI

- Replace terminal UI with graphical interface
- Keep audio and session components unchanged
- Modular design allows UI swap without touching audio/AI logic

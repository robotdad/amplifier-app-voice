# DDD Plan: Amplifier Voice Assistant App

## Problem Statement

**What we're solving**: The OpenAI Realtime provider works but has no application to demonstrate it. Users need a simple way to have voice conversations with AI.

**Why it matters**: Validates the provider in a real application. Makes voice AI accessible through a simple desktop tool.

**User value**:
- Natural voice conversation with AI (speak and hear responses)
- Simple interaction (press spacebar to talk)
- Live feedback (see transcription of conversation)
- Easy to use (uvx installable, minimal setup)
- Works offline-first (desktop app, not web-dependent)

**Target use case**: Exploratory voice assistant for desktop. Developers and early adopters testing OpenAI Realtime API capabilities.

## Proposed Solution

**High-level approach**: Simple Python desktop application using PyAudio for microphone/speaker I/O, keyboard library for press-to-talk detection, Rich for terminal UI, and Amplifier with our new Realtime provider for AI conversation.

**Key workflow**:
```
1. User launches: amplifier-voice
2. Terminal shows: "Press SPACE to talk..."
3. User holds SPACE → mic records
4. User releases SPACE → recording stops, sends to OpenAI
5. Model responds → audio plays through speakers
6. Transcript shows in terminal
7. Repeat
```

**Architecture**:
```
┌─────────────────────────────────────────┐
│  Terminal UI (Rich)                     │
│  - Show transcripts                     │
│  - Show status                          │
│  - Keyboard input                       │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Main Loop                              │
│  - Detect spacebar press/release        │
│  - Coordinate audio capture/playback    │
│  - Manage Amplifier session             │
└─────────────┬───────────────────────────┘
              │
        ┌─────┴─────┐
        ▼           ▼
┌──────────────┐ ┌──────────────────────┐
│ Audio I/O    │ │ Amplifier Session    │
│ - PyAudio    │ │ - Realtime provider  │
│ - Capture    │ │ - Send text prompts  │
│ - Playback   │ │ - Receive responses  │
└──────────────┘ └──────────────────────┘
```

## Architecture & Design

### Key Interfaces

**CLI Entry Point**:
```python
@click.command()
@click.option("--voice", default="alloy", help="Voice selection")
@click.option("--temperature", default=0.7, help="Response randomness")
@click.option("--model", help="Model override")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(voice, temperature, model, debug):
    """Launch voice assistant."""
```

**Audio Capture** (audio/capture.py):
```python
class AudioCapture:
    def start_recording(self) -> None:
        """Start recording from microphone."""

    def stop_recording(self) -> bytes:
        """Stop recording and return PCM16 audio data."""
```

**Audio Playback** (audio/playback.py):
```python
class AudioPlayback:
    def play(self, audio_data: bytes) -> None:
        """Play PCM16 audio through speakers."""
```

**Terminal UI** (ui/terminal.py):
```python
class TerminalUI:
    def show_status(self, message: str) -> None:
        """Display status message."""

    def show_transcript(self, role: str, text: str) -> None:
        """Display conversation transcript."""

    def wait_for_spacebar(self) -> bool:
        """Wait for spacebar press, return True when pressed."""
```

### Module Boundaries

**What amplifier-app-voice owns**:
- Audio capture from microphone (PyAudio)
- Audio playback through speakers (PyAudio)
- Keyboard input detection (pynput or keyboard library)
- Terminal UI rendering (Rich)
- Application loop and state management
- Configuration file loading

**What amplifier-app-voice does NOT own**:
- Audio format conversion (provider handles PCM16)
- OpenAI protocol (provider handles WebSocket)
- Tool execution (Amplifier core handles)
- Session management (provider handles)

**Clear "studs"** (connection points):
1. PyAudio → Raw PCM16 audio bytes
2. Amplifier provider → Text prompts in, audio responses out
3. Keyboard → Spacebar press/release events
4. Rich console → Terminal rendering

### Data Models

**Configuration**:
```python
@dataclass
class AppConfig:
    # OpenAI settings
    api_key: str
    model: str = "gpt-4o-realtime-preview-2024-12-17"
    voice: str = "alloy"
    temperature: float = 0.7

    # Audio settings
    input_device: int | None = None  # None = default
    output_device: int | None = None
    sample_rate: int = 24000

    # UI settings
    show_transcripts: bool = True
    show_audio_levels: bool = False
```

**Application State**:
```python
@dataclass
class AppState:
    recording: bool = False
    conversation_history: list[tuple[str, str]] = field(default_factory=list)  # (role, text)
    session: AmplifierSession | None = None
```

## Files to Change

### Non-Code Files (Phase 2)

**Already created (need updates)**:
- [ ] README.md - Update with actual usage (already has good structure)
- [ ] CHANGELOG.md - Document initial release

**To create**:
- [ ] docs/ARCHITECTURE.md - App design and component overview
- [ ] docs/AUDIO_SETUP.md - PyAudio setup and troubleshooting
- [ ] docs/KEYBOARD_CONTROLS.md - Interaction controls
- [ ] docs/CONFIGURATION.md - Config file reference
- [ ] examples/simple_conversation.sh - Quick start script
- [ ] examples/config.yaml - Example configuration

### Code Files (Phase 4)

**To create in src/amplifier_app_voice/**:

- [ ] main.py - CLI entry point, Click setup, main loop
- [ ] config.py - Configuration loading (YAML + env + CLI args)
- [ ] session_manager.py - Amplifier session creation and management
- [ ] audio/capture.py - Microphone recording with PyAudio
- [ ] audio/playback.py - Speaker playback with PyAudio
- [ ] audio/utils.py - Audio utilities (device listing, format conversion)
- [ ] ui/terminal.py - Rich terminal UI (status, transcripts)
- [ ] ui/keyboard.py - Spacebar detection (pynput or keyboard library)

**To create in tests/**:

- [ ] test_audio_capture.py - Audio capture tests (may need real mic)
- [ ] test_audio_playback.py - Audio playback tests (may need real speakers)
- [ ] test_config.py - Configuration loading tests
- [ ] test_integration.py - End-to-end test (requires mic, speakers, API key)

## Philosophy Alignment

### Ruthless Simplicity

**Start minimal**:
- ✅ Press-to-talk only (no VAD)
- ✅ Terminal UI only (no GUI)
- ✅ Default audio devices (no device selection UI initially)
- ✅ Text prompts to provider (provider handles audio conversion)
- ✅ Simple state (recording boolean, conversation history list)

**Avoid future-proofing**:
- ❌ NOT building: Wake word detection
- ❌ NOT building: Continuous listening
- ❌ NOT building: Multi-user support
- ❌ NOT building: Rich GUI
- ❌ NOT building: Audio preprocessing/effects

**Clear over clever**:
- Direct PyAudio usage (no abstraction layers)
- Simple keyboard detection (just spacebar)
- Straightforward terminal output (Rich console.print)
- Linear main loop (no complex state machine)

### Modular Design

**Bricks** (self-contained modules):
- `audio/capture.py` - Microphone recording
- `audio/playback.py` - Speaker playback
- `ui/terminal.py` - Terminal display
- `ui/keyboard.py` - Keyboard input
- `config.py` - Configuration management
- `session_manager.py` - Amplifier session wrapper
- `main.py` - Application orchestration

**Studs** (interfaces):
- `AudioCapture.start_recording()` / `.stop_recording() -> bytes`
- `AudioPlayback.play(bytes)`
- `TerminalUI.show_status(str)` / `.show_transcript(role, text)`
- `Keyboard.wait_for_press()` / `.wait_for_release()`
- `AmplifierSession.execute(prompt) -> response`

**Regeneratable**:
- Each module can be rebuilt from spec
- Clear dependencies (main → audio/ui, audio → PyAudio, ui → Rich)
- No circular imports

## Test Strategy

### Validation Approach (Not Traditional TDD)

**Primary validation**: Actually run the app and talk to it

**Integration test**:
```bash
# THE test that matters
amplifier-voice
# Press spacebar, say "Hello", release, hear response

# If that works, app works!
```

**Automated tests** (minimal):
- Configuration loading works
- Audio format is correct (PCM16, 24kHz)
- Session creates successfully
- **No mocking** - we'll validate with real usage

**Add tests only if**:
- We discover edge cases during real usage
- Need to prevent regressions
- Testing actual runtime invariants

### User Testing

**Manual verification**:
1. Install app: `uv pip install -e .`
2. Run: `amplifier-voice`
3. Press spacebar and say "Hello"
4. Verify:
   - Recording starts (UI shows status)
   - Recording stops when release spacebar
   - Audio sent to OpenAI
   - Response plays through speakers
   - Transcript appears in terminal
5. Test multi-turn conversation (3-5 exchanges)
6. Test with different voices (`--voice marin`)

**Success criteria**:
- App launches without errors
- Mic capture works
- Speaker playback works
- Conversation flows naturally
- Transcripts are accurate
- Multiple turns work

## Implementation Approach

### Phase 2 (Documentation)

**Order** (high-level → details):

1. README.md - Update with actual usage examples
2. docs/ARCHITECTURE.md - Component design
3. docs/AUDIO_SETUP.md - PyAudio installation and troubleshooting
4. docs/KEYBOARD_CONTROLS.md - Interaction reference
5. docs/CONFIGURATION.md - Config file format
6. examples/ - Quick start scripts and config
7. CHANGELOG.md - Initial release notes

### Phase 4 (Code Implementation)

**Chunks** (dependency order):

**Chunk 1: Configuration & Session**
- config.py (load YAML, env, CLI args)
- session_manager.py (create Amplifier session with provider)
- No dependencies, foundation for others

**Chunk 2: Audio I/O**
- audio/utils.py (device listing, validation)
- audio/capture.py (PyAudio recording)
- audio/playback.py (PyAudio playback)
- Depends on: config (for device selection)

**Chunk 3: Terminal UI**
- ui/terminal.py (Rich console display)
- ui/keyboard.py (spacebar detection)
- Depends on: Nothing (standalone UI)

**Chunk 4: Main Application**
- main.py (CLI, main loop, orchestration)
- Depends on: Chunks 1, 2, 3 (ties everything together)

**Validation after Chunk 4**: Run the app with real mic/speakers/API

## Success Criteria

### Functional Requirements
- ✅ App launches successfully
- ✅ Press spacebar starts recording
- ✅ Release spacebar stops and sends
- ✅ Audio plays through speakers
- ✅ Transcripts display in terminal
- ✅ Multiple conversation turns work
- ✅ Different voices selectable via CLI

### Non-Functional Requirements
- ✅ Latency acceptable (<3 seconds typical)
- ✅ Audio quality good (clear speech)
- ✅ Terminal UI responsive
- ✅ Graceful error handling
- ✅ Clean exit (Ctrl+C works)

### Philosophy Requirements
- ✅ Ruthless simplicity (minimal features)
- ✅ Clear module boundaries
- ✅ Direct library usage (no unnecessary wrappers)
- ✅ Works with validation, not extensive testing

## Risks & Mitigations

### Risk 1: PyAudio Installation Issues
**Issue**: PyAudio requires system dependencies (portaudio)

**Mitigation**:
- Document installation clearly (brew install, apt-get, etc.)
- Provide troubleshooting guide
- Test on multiple platforms (macOS, Linux, Windows)
- Consider fallback to sounddevice library if PyAudio problematic

### Risk 2: Keyboard Detection Complexity
**Issue**: Cross-platform keyboard detection can be tricky

**Mitigation**:
- Start with pynput library (cross-platform)
- Simple spacebar-only detection (not complex hotkeys)
- Fallback to polling if event-based detection fails
- Document keyboard permissions (macOS requires accessibility)

### Risk 3: Audio Device Selection
**Issue**: Users may have multiple mics/speakers

**Mitigation**:
- Default to system default device (works for most)
- Provide device listing utility
- Support device selection via config file
- Don't build device selection UI initially

### Risk 4: Provider Not Installed
**Issue**: App requires amplifier-module-provider-openai-realtime

**Mitigation**:
- Document provider installation clearly
- Check at startup, give helpful error if missing
- Consider bundling provider as dependency (if possible)

## Design Decisions

### Decision 1: Text Prompts to Provider

**Question**: Should app send text or audio to provider?

**Answer**: **Text prompts**

**Rationale**:
- Provider validated to work with text input
- Simpler than audio conversion
- Provider handles text→audio conversation internally
- Follows validation results from provider testing

### Decision 2: Press-to-Talk vs Always-On

**Question**: How should recording be triggered?

**Answer**: **Press-to-talk (spacebar)**

**Rationale**:
- Simple and predictable
- No false activations
- Clear recording boundaries
- Less CPU (only record when pressed)

### Decision 3: Terminal UI vs GUI

**Question**: What UI framework?

**Answer**: **Terminal (Rich library)**

**Rationale**:
- Much simpler to build
- Faster to iterate
- Easier to distribute (no GUI dependencies)
- Good enough for exploratory phase

### Decision 4: Synchronous vs Async Main Loop

**Question**: Should main loop be async or threaded?

**Answer**: **Async with asyncio**

**Rationale**:
- Amplifier sessions are async
- PyAudio callbacks can trigger async events
- Simpler than threading
- Better resource management

## Next Steps

✅ **Plan complete**

**Key points to confirm**:
1. Press-to-talk interaction acceptable?
2. Terminal UI sufficient (no GUI needed)?
3. Text prompts to provider confirmed?
4. PyAudio for audio I/O confirmed?

**When approved, proceed to**: `/ddd:2-docs`

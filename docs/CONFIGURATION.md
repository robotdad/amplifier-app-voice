# Configuration Reference

Complete configuration guide for amplifier-app-voice.

## Configuration File

**Location**: `~/.config/amplifier-voice/config.yaml`

**Format**: YAML

### Full Example

```yaml
# OpenAI Realtime API settings
openai:
  api_key: ${OPENAI_API_KEY}  # Or literal key (not recommended)
  model: gpt-4o-realtime-preview-2024-12-17
  voice: alloy
  temperature: 0.7
  max_response_tokens: null  # null = unlimited

# Audio input/output settings
audio:
  input_device: null   # null = system default microphone
  output_device: null  # null = system default speakers
  sample_rate: 24000   # OpenAI Realtime requirement
  buffer_size: 1024    # Audio buffer size in frames
  max_recording_duration: 30  # Maximum seconds per recording

# Terminal UI settings
ui:
  show_transcripts: true        # Display conversation text
  show_audio_levels: false      # Show mic level meter (future)
  show_timestamps: false        # Show message timestamps
  theme: dark                   # dark or light
```

## Configuration Sections

### OpenAI Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | str | `$OPENAI_API_KEY` | OpenAI API key (use env var) |
| `model` | str | `gpt-4o-realtime-preview-2024-12-17` | Model to use |
| `voice` | str | `alloy` | Voice selection (alloy, echo, shimmer, marin, cedar) |
| `temperature` | float | `0.7` | Response randomness (0.0-1.0) |
| `max_response_tokens` | int\|null | `null` | Optional output limit |

### Audio Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `input_device` | int\|null | `null` | Microphone device index |
| `output_device` | int\|null | `null` | Speaker device index |
| `sample_rate` | int | `24000` | Sample rate (must be 24000 for OpenAI) |
| `buffer_size` | int | `1024` | Audio buffer size in frames |
| `max_recording_duration` | int | `30` | Max seconds per recording |

**Device indices**: Run `python -m amplifier_app_voice.audio.utils --list-devices` to see available devices.

### UI Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `show_transcripts` | bool | `true` | Display conversation text |
| `show_audio_levels` | bool | `false` | Show mic level meter |
| `show_timestamps` | bool | `false` | Show message timestamps |
| `theme` | str | `dark` | Terminal theme (dark or light) |

## Configuration Priority

Settings are loaded in order (later overrides earlier):

1. **Default values** (hardcoded in app)
2. **Config file** (`~/.config/amplifier-voice/config.yaml`)
3. **Environment variables** (e.g., `OPENAI_API_KEY`)
4. **Command-line flags** (e.g., `--voice marin`)

### Example

```yaml
# config.yaml
openai:
  voice: alloy
```

```bash
# Environment
export OPENAI_API_KEY="sk-..."

# Command line
amplifier-voice --voice marin
```

**Result**: voice = `marin` (CLI override wins)

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key (recommended over config file) |
| `AMPLIFIER_VOICE_CONFIG` | Override config file location |

## Command-Line Options

```bash
amplifier-voice --help
```

**Available options**:
- `--voice TEXT` - Voice selection
- `--temperature FLOAT` - Response randomness
- `--model TEXT` - Model override
- `--input-device INTEGER` - Microphone device index
- `--output-device INTEGER` - Speaker device index
- `--config PATH` - Config file location
- `--debug` - Enable debug logging

## Creating Config File

**Option 1: Manual**

```bash
mkdir -p ~/.config/amplifier-voice
cat > ~/.config/amplifier-voice/config.yaml << 'EOF'
openai:
  api_key: ${OPENAI_API_KEY}
  voice: alloy

audio:
  input_device: null
  output_device: null
EOF
```

**Option 2: Copy Example**

```bash
mkdir -p ~/.config/amplifier-voice
cp examples/config.yaml ~/.config/amplifier-voice/config.yaml
# Edit as needed
```

## See Also

- [Audio Setup](AUDIO_SETUP.md) - Audio device configuration
- [Architecture](ARCHITECTURE.md) - How configuration is used
- [examples/config.yaml](../examples/config.yaml) - Example config file

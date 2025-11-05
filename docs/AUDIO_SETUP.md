# Audio Setup Guide

Complete guide to setting up audio for amplifier-app-voice.

## System Requirements

### PortAudio Installation

amplifier-app-voice uses PyAudio, which requires PortAudio system library.

**macOS**:
```bash
brew install portaudio
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
```

**Linux (Fedora/RHEL)**:
```bash
sudo dnf install portaudio-devel
```

**Windows**:
- PyAudio wheels include PortAudio
- No system dependencies needed

### Python Dependencies

After PortAudio is installed:

```bash
# Install amplifier-app-voice (includes PyAudio)
uv pip install git+https://github.com/robotdad/amplifier-app-voice@main
```

## Audio Device Configuration

### List Available Devices

```bash
python -c "
import pyaudio
p = pyaudio.PyAudio()
print('Available audio devices:')
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f'{i}: {info[\"name\"]} (in:{info[\"maxInputChannels\"]}, out:{info[\"maxOutputChannels\"]})')
p.terminate()
"
```

### Select Specific Devices

Edit `~/.config/amplifier-voice/config.yaml`:

```yaml
audio:
  input_device: 2   # Microphone device index
  output_device: 4  # Speaker device index
  sample_rate: 24000
```

**Note**: `null` or omitted means use system default device.

## Troubleshooting

### "No module named 'pyaudio'"

**Solution**:
```bash
# Ensure PortAudio installed first
brew install portaudio  # macOS

# Then install PyAudio
pip install pyaudio
```

### "Input overflow" / "Output underflow"

**Cause**: Buffer size mismatch with audio device

**Solution**: Increase buffer size in config:
```yaml
audio:
  buffer_size: 2048  # Default is 1024
```

### "No default input device"

**Cause**: No microphone available or permissions denied

**macOS Solution**:
- System Settings → Privacy & Security → Microphone
- Enable access for Terminal (or your terminal app)

**Linux Solution**:
```bash
# Check microphone is detected
arecord -l

# Test recording
arecord -d 5 test.wav
aplay test.wav
```

### "Device busy" or "Device not available"

**Cause**: Another application using audio device

**Solution**:
- Close other apps using microphone (Zoom, Discord, etc.)
- Restart amplifier-voice
- Try different device index

## Testing Audio Setup

### Test Microphone

```bash
python -c "
import pyaudio
import numpy as np

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=24000, input=True, frames_per_buffer=1024)

print('Recording 3 seconds...')
frames = [stream.read(1024) for _ in range(int(24000/1024 * 3))]
stream.close()
p.terminate()

print(f'Captured {len(b\"\".join(frames))} bytes')
"
```

### Test Speakers

```bash
python -c "
import pyaudio
import numpy as np

# Generate 1 second tone at 440Hz
t = np.linspace(0, 1, 24000, endpoint=False)
audio = (np.sin(2 * np.pi * 440 * t) * 32767 * 0.5).astype(np.int16)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

print('Playing tone...')
stream.write(audio.tobytes())

stream.close()
p.terminate()
"
```

## See Also

- [Architecture](ARCHITECTURE.md) - Component design
- [Configuration](CONFIGURATION.md) - Config file reference
- [Keyboard Controls](KEYBOARD_CONTROLS.md) - Interaction guide

"""Audio device utilities for amplifier-app-voice."""

import pyaudio


def list_audio_devices() -> None:
    """List all available audio devices with their capabilities."""
    p = pyaudio.PyAudio()

    print("\nAvailable audio devices:")
    print("-" * 80)

    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        input_channels = info["maxInputChannels"]
        output_channels = info["maxOutputChannels"]

        device_type = []
        if input_channels > 0:
            device_type.append(f"input:{input_channels}")
        if output_channels > 0:
            device_type.append(f"output:{output_channels}")

        capabilities = ", ".join(device_type) if device_type else "no channels"

        print(f"{i:2d}: {info['name']}")
        print(f"    {capabilities}")
        print(f"    Sample rate: {int(info['defaultSampleRate'])} Hz")
        print()

    p.terminate()


def main() -> None:
    """CLI entry point for device listing."""
    import sys

    if "--list-devices" in sys.argv:
        list_audio_devices()
    else:
        print("Usage: python -m amplifier_app_voice.audio.utils --list-devices")
        sys.exit(1)


if __name__ == "__main__":
    main()

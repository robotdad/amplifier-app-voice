"""Audio playback for amplifier-app-voice."""

import pyaudio


class AudioPlayback:
    """Plays audio through speakers using PyAudio.

    Handles PCM16 audio at 24kHz mono, matching OpenAI Realtime API format.
    Playback is blocking - waits for audio to complete before returning.
    """

    def __init__(self, device_index: int | None = None, sample_rate: int = 24000) -> None:
        """Initialize audio playback.

        Args:
            device_index: Output device index (None = system default)
            sample_rate: Sample rate in Hz (default: 24000 for OpenAI)
        """
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.p = pyaudio.PyAudio()

    def play(self, audio_data: bytes) -> None:
        """Play PCM16 audio through speakers (blocking).

        Args:
            audio_data: PCM16 audio data as bytes
        """
        stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            output=True,
            output_device_index=self.device_index,
        )

        stream.write(audio_data)
        stream.stop_stream()
        stream.close()

    def cleanup(self) -> None:
        """Release PyAudio resources.

        Should be called when done with playback to free system resources.
        """
        self.p.terminate()

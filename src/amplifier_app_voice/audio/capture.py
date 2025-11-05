"""Audio capture for amplifier-app-voice."""

import pyaudio


class AudioCapture:
    """Captures audio from microphone using PyAudio.

    Uses callback-based recording for low latency. Captures PCM16 audio
    at 24kHz mono, matching OpenAI Realtime API requirements.
    """

    def __init__(self, device_index: int | None = None, sample_rate: int = 24000, buffer_size: int = 1024) -> None:
        """Initialize audio capture.

        Args:
            device_index: Input device index (None = system default)
            sample_rate: Sample rate in Hz (default: 24000 for OpenAI)
            buffer_size: Buffer size in frames (default: 1024)
        """
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.p = pyaudio.PyAudio()
        self.stream: pyaudio.Stream | None = None
        self.frames: list[bytes] = []
        self.is_recording = False

    def start_recording(self) -> None:
        """Start recording from microphone.

        Opens PyAudio stream with callback for low-latency capture.
        Clears any existing frames before starting.
        """
        self.frames = []
        self.is_recording = True

        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.buffer_size,
            stream_callback=self._callback,
        )

        self.stream.start_stream()

    def _callback(self, in_data: bytes, frame_count: int, time_info: dict, status: int) -> tuple[None, int]:
        """Callback for audio stream.

        Args:
            in_data: Audio data from microphone
            frame_count: Number of frames
            time_info: Timing information
            status: Stream status

        Returns:
            Tuple of (None, continue flag)
        """
        if self.is_recording:
            self.frames.append(in_data)
        return (None, pyaudio.paContinue)

    def stop_recording(self) -> bytes:
        """Stop recording and return captured audio data.

        Returns:
            PCM16 audio data as bytes
        """
        self.is_recording = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        return b"".join(self.frames)

    def cleanup(self) -> None:
        """Release PyAudio resources.

        Should be called when done with capture to free system resources.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        self.p.terminate()

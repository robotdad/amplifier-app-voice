"""Keyboard input handling using pynput for toggle-based recording control."""

import asyncio

from pynput import keyboard


class KeyboardHandler:
    """Handles keyboard input with spacebar toggle (press to start, press again to stop)."""

    def __init__(self: "KeyboardHandler") -> None:
        """Initialize keyboard handler and async events."""
        self.recording = False
        self._running = False
        self._listener: keyboard.Listener | None = None
        self._start_event = asyncio.Event()
        self._stop_event = asyncio.Event()
        self._loop: asyncio.AbstractEventLoop | None = None

    def start(self: "KeyboardHandler") -> None:
        """Start keyboard detection in background thread."""
        self._running = True
        self._loop = asyncio.get_event_loop()
        
        # Start pynput keyboard listener
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.start()

    def _on_press(self: "KeyboardHandler", key) -> None:
        """Handle key press event - toggle recording on/off.
        
        Args:
            key: Key object from pynput
        """
        try:
            # Check if spacebar pressed - toggle recording state
            if key == keyboard.Key.space:
                if not self.recording:
                    # Start recording
                    self.recording = True
                    if self._loop:
                        self._loop.call_soon_threadsafe(self._start_event.set)
                else:
                    # Stop recording
                    self.recording = False
                    if self._loop:
                        self._loop.call_soon_threadsafe(self._stop_event.set)
        except Exception:
            pass  # Ignore errors

    async def wait_for_press(self: "KeyboardHandler") -> None:
        """Wait for spacebar press to start recording (async)."""
        self._start_event.clear()
        await self._start_event.wait()

    async def wait_for_release(self: "KeyboardHandler") -> None:
        """Wait for spacebar press to stop recording (async)."""
        self._stop_event.clear()
        await self._stop_event.wait()

    def stop(self: "KeyboardHandler") -> None:
        """Stop keyboard listener."""
        self._running = False
        if self._listener:
            self._listener.stop()
            self._listener = None

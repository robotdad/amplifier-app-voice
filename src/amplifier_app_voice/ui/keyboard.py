"""Keyboard input handling using readchar for terminal-specific detection."""

import asyncio
import threading

import readchar


class KeyboardHandler:
    """Handles keyboard input with spacebar detection in terminal."""

    def __init__(self: "KeyboardHandler") -> None:
        """Initialize keyboard handler and async events."""
        self.space_pressed = False
        self._running = False
        self._thread: threading.Thread | None = None
        self._press_event = asyncio.Event()
        self._release_event = asyncio.Event()
        self._loop: asyncio.AbstractEventLoop | None = None

    def start(self: "KeyboardHandler") -> None:
        """Start keyboard detection in background thread."""
        self._running = True
        self._loop = asyncio.get_event_loop()
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _read_loop(self: "KeyboardHandler") -> None:
        """Background thread reading keyboard input."""
        while self._running:
            try:
                key = readchar.readkey()
                if key == " ":  # Spacebar
                    if not self.space_pressed:
                        # Press event
                        self.space_pressed = True
                        if self._loop:
                            self._loop.call_soon_threadsafe(self._press_event.set)
                    else:
                        # Release event (second space = release)
                        self.space_pressed = False
                        if self._loop:
                            self._loop.call_soon_threadsafe(self._release_event.set)
            except Exception:
                pass  # Ignore read errors

    async def wait_for_press(self: "KeyboardHandler") -> None:
        """Wait for spacebar press (async)."""
        self._press_event.clear()
        await self._press_event.wait()

    async def wait_for_release(self: "KeyboardHandler") -> None:
        """Wait for spacebar release (async)."""
        self._release_event.clear()
        await self._release_event.wait()

    def stop(self: "KeyboardHandler") -> None:
        """Stop keyboard listener."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

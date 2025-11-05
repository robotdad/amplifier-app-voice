"""Keyboard input handling using pynput for cross-platform detection."""

import asyncio

from pynput import keyboard


class KeyboardHandler:
    """Handles keyboard input with spacebar detection."""

    def __init__(self: "KeyboardHandler") -> None:
        """Initialize keyboard listener and async events."""
        self.space_pressed = False
        self.listener: keyboard.Listener | None = None
        self._press_event = asyncio.Event()
        self._release_event = asyncio.Event()

    def start(self: "KeyboardHandler") -> None:
        """Start keyboard listener in background thread."""
        self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self.listener.start()

    def _on_press(self: "KeyboardHandler", key: keyboard.Key | keyboard.KeyCode | None) -> None:
        """Handle key press events.

        Args:
            key: Key that was pressed
        """
        if key == keyboard.Key.space and not self.space_pressed:
            self.space_pressed = True
            self._press_event.set()

    def _on_release(self: "KeyboardHandler", key: keyboard.Key | keyboard.KeyCode | None) -> None:
        """Handle key release events.

        Args:
            key: Key that was released
        """
        if key == keyboard.Key.space:
            self.space_pressed = False
            self._release_event.set()

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
        if self.listener:
            self.listener.stop()

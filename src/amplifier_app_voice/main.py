"""Main application entry point and event loop for amplifier-app-voice."""

import asyncio
import sys
from pathlib import Path

import click

from .audio.capture import AudioCapture
from .audio.playback import AudioPlayback
from .config import AppConfig
from .config import load_config
from .session_manager import SessionManager
from .ui.keyboard import KeyboardHandler
from .ui.terminal import TerminalUI


@click.command()
@click.option("--voice", help="Voice selection (alloy, echo, shimmer, marin, cedar)")
@click.option("--temperature", type=float, help="Response randomness (0.0-1.0)")
@click.option("--model", help="Model override")
@click.option("--input-device", type=int, help="Input device index")
@click.option("--output-device", type=int, help="Output device index")
@click.option("--config", type=click.Path(), help="Config file path")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(
    voice: str | None,
    temperature: float | None,
    model: str | None,
    input_device: int | None,
    output_device: int | None,
    config: str | None,
    debug: bool,
) -> None:
    """Launch Amplifier voice assistant.

    Press SPACE to talk, release to send. Press Ctrl+C to exit.
    """
    # Build CLI overrides dict from Click options
    cli_overrides = {}
    if voice:
        cli_overrides["voice"] = voice
    if temperature is not None:
        cli_overrides["temperature"] = temperature
    if model:
        cli_overrides["model"] = model
    if input_device is not None:
        cli_overrides["input_device"] = input_device
    if output_device is not None:
        cli_overrides["output_device"] = output_device

    # Load configuration with priority: defaults < YAML < env vars < CLI args
    config_path = Path(config) if config else None
    try:
        app_config = load_config(config_path, cli_overrides)
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)

    # Run async main loop
    asyncio.run(async_main(app_config, debug))


async def async_main(config: AppConfig, debug: bool = False) -> None:
    """Async main event loop.

    Args:
        config: Application configuration
        debug: Enable debug logging if True
    """
    # Initialize all components
    ui = TerminalUI()
    keyboard_handler = KeyboardHandler()
    audio_capture = AudioCapture(
        device_index=config.input_device,
        sample_rate=config.sample_rate,
        buffer_size=config.buffer_size,
    )
    audio_playback = AudioPlayback(
        device_index=config.output_device,
        sample_rate=config.sample_rate,
    )
    session_mgr = SessionManager(config)

    try:
        # Show welcome message
        ui.show_welcome()

        # Create Amplifier session with Realtime provider
        session = await session_mgr.create_session()
        ui.show_status("Session created", "green")

        # Start keyboard listener
        keyboard_handler.start()
        ui.show_status("Press SPACE to talk...", "green")

        # Main loop
        while True:
            # Wait for spacebar press
            await keyboard_handler.wait_for_press()

            # Start audio recording
            audio_capture.start_recording()
            ui.show_status("🎤 Recording...", "yellow")

            # Wait for spacebar release
            await keyboard_handler.wait_for_release()

            # Stop recording
            audio_data = audio_capture.stop_recording()
            ui.clear_status()
            ui.show_status("⏳ Sending to AI...", "cyan")

            # Send actual audio to OpenAI Realtime API
            # Access provider directly since session.execute() doesn't support audio yet
            try:
                # Get the provider from session coordinator
                provider = session.coordinator.mount_points["providers"].get("openai-realtime")

                if provider:
                    # Call provider with audio message
                    audio_message = {
                        "role": "user",
                        "content": [{"type": "audio", "data": audio_data, "format": "pcm16", "sample_rate": 24000}],
                    }

                    # Call provider directly with audio
                    provider_response = await provider.complete([audio_message])

                    # Extract transcript
                    transcript = provider_response.content

                    # Display transcript
                    if config.show_transcripts:
                        ui.show_transcript("assistant", transcript)

                    # Play audio response
                    if provider_response.raw and "audio_data" in provider_response.raw:
                        ui.show_status("🔊 Playing response...", "magenta")
                        audio_playback.play(provider_response.raw["audio_data"])
                    else:
                        ui.show_status("🔊 Response received (no audio)", "magenta")
                else:
                    ui.show_status("❌ Provider not found", "red")

            except Exception as e:
                ui.show_status(f"❌ Error: {e}", "red")

            # Ready for next input
            ui.show_status("Press SPACE to talk...", "green")

    except KeyboardInterrupt:
        ui.show_status("\nGoodbye!", "green")
    finally:
        # Cleanup all resources
        keyboard_handler.stop()
        audio_capture.cleanup()
        audio_playback.cleanup()
        await session_mgr.close()


if __name__ == "__main__":
    main()

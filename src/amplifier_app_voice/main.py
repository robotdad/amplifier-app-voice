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

    Press SPACE to start talking, press SPACE again to stop and send. Press Ctrl+C to exit.
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
        
        # Emit app initialization event
        if session and hasattr(session, "coordinator") and hasattr(session.coordinator, "hooks"):
            await session.coordinator.hooks.emit(
                "app:initialized",
                {
                    "session_id": session_mgr.session_id,
                    "application": "amplifier-app-voice",
                    "input_device": config.input_device,
                    "output_device": config.output_device,
                    "sample_rate": config.sample_rate,
                },
            )

        # Start keyboard listener
        keyboard_handler.start()
        ui.show_status("Press SPACE to start talking...", "green")

        # Main loop
        while True:
            # Wait for spacebar press to start
            await keyboard_handler.wait_for_press()

            # Start audio recording
            audio_capture.start_recording()
            ui.show_status("🎤 Recording... (press SPACE again to stop)", "yellow")
            
            # Emit recording start event
            if session and hasattr(session, "coordinator") and hasattr(session.coordinator, "hooks"):
                await session.coordinator.hooks.emit(
                    "audio:recording:start",
                    {
                        "session_id": session_mgr.session_id,
                        "sample_rate": config.sample_rate,
                    },
                )

            # Wait for spacebar press again to stop
            await keyboard_handler.wait_for_release()

            # Stop recording
            audio_data = audio_capture.stop_recording()
            audio_duration_ms = len(audio_data) / (config.sample_rate * 2) * 1000  # PCM16 = 2 bytes per sample
            
            # Emit recording complete event
            if session and hasattr(session, "coordinator") and hasattr(session.coordinator, "hooks"):
                await session.coordinator.hooks.emit(
                    "audio:recording:complete",
                    {
                        "session_id": session_mgr.session_id,
                        "duration_ms": int(audio_duration_ms),
                        "bytes": len(audio_data),
                    },
                )
            
            ui.clear_status()
            ui.show_status("⏳ Sending to AI...", "cyan")

            # Send actual audio to OpenAI Realtime API
            # Access provider directly since session.execute() doesn't support audio yet
            try:
                # Get the provider from session coordinator
                provider = session.coordinator.mount_points["providers"].get("openai-realtime")

                if provider:
                    # Build messages with system instruction for English responses
                    messages = [
                        {
                            "role": "system",
                            "content": "You are a helpful voice assistant. Always respond in English. Be concise, conversational, and friendly. When answering questions, provide clear and direct responses appropriate for voice interaction."
                        },
                        {
                            "role": "user",
                            "content": [{"type": "audio", "data": audio_data, "format": "pcm16", "sample_rate": 24000}],
                        }
                    ]

                    # Call provider directly with audio (provider emits provider:request and provider:response hooks)
                    provider_response = await provider.complete(messages)

                    # Extract transcript
                    transcript = provider_response.content
                    
                    # Log user input to transcript.jsonl (we don't have the user's actual words, just audio)
                    session_mgr.write_transcript(
                        "user",
                        "[audio input]",
                        audio_metadata={
                            "format": "pcm16",
                            "sample_rate": 24000,
                            "duration_ms": int(audio_duration_ms),
                            "bytes": len(audio_data),
                        },
                    )

                    # Log assistant response to transcript.jsonl
                    session_mgr.write_transcript(
                        "assistant",
                        transcript,
                        audio_metadata={
                            "format": provider_response.raw.get("audio_format", "pcm16"),
                            "sample_rate": provider_response.raw.get("sample_rate", 24000),
                        } if provider_response.raw and "audio_data" in provider_response.raw else None,
                    )

                    # Display transcript
                    if config.show_transcripts:
                        ui.show_transcript("assistant", transcript)

                    # Play audio response
                    if provider_response.raw and "audio_data" in provider_response.raw:
                        ui.show_status("🔊 Playing response...", "magenta")
                        
                        # Emit playback start event
                        if session and hasattr(session, "coordinator") and hasattr(session.coordinator, "hooks"):
                            await session.coordinator.hooks.emit(
                                "audio:playback:start",
                                {
                                    "session_id": session_mgr.session_id,
                                    "audio_format": provider_response.raw.get("audio_format", "pcm16"),
                                    "sample_rate": provider_response.raw.get("sample_rate", 24000),
                                },
                            )
                        
                        audio_playback.play(provider_response.raw["audio_data"])
                        
                        # Emit playback complete event
                        if session and hasattr(session, "coordinator") and hasattr(session.coordinator, "hooks"):
                            await session.coordinator.hooks.emit(
                                "audio:playback:complete",
                                {
                                    "session_id": session_mgr.session_id,
                                },
                            )
                    else:
                        ui.show_status("🔊 Response received (no audio)", "magenta")
                else:
                    ui.show_status("❌ Provider not found", "red")
                    
                    # Emit error event
                    if session and hasattr(session, "coordinator") and hasattr(session.coordinator, "hooks"):
                        await session.coordinator.hooks.emit(
                            "app:error",
                            {
                                "session_id": session_mgr.session_id,
                                "error_type": "ProviderNotFound",
                                "error_message": "openai-realtime provider not found in session",
                            },
                        )

            except Exception as e:
                ui.show_status(f"❌ Error: {e}", "red")
                
                # Emit error event
                if session and hasattr(session, "coordinator") and hasattr(session.coordinator, "hooks"):
                    await session.coordinator.hooks.emit(
                        "app:error",
                        {
                            "session_id": session_mgr.session_id,
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                        },
                    )

            # Ready for next input
            ui.show_status("Press SPACE to start talking...", "green")

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

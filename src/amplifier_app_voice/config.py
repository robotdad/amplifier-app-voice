"""Configuration loading and management for amplifier-app-voice."""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class AppConfig:
    """Application configuration matching docs/CONFIGURATION.md schema."""

    # OpenAI settings
    api_key: str
    model: str = "gpt-4o-realtime-preview-2024-12-17"
    voice: str = "alloy"
    temperature: float = 0.7
    max_response_tokens: int | None = None

    # Audio settings
    input_device: int | None = None
    output_device: int | None = None
    sample_rate: int = 24000
    buffer_size: int = 1024
    max_recording_duration: int = 30

    # UI settings
    show_transcripts: bool = True
    show_audio_levels: bool = False
    show_timestamps: bool = False
    theme: str = "dark"


def load_config(config_path: Path | None = None, cli_overrides: dict | None = None) -> AppConfig:
    """
    Load configuration with priority: defaults < file < env < CLI.

    Args:
        config_path: Path to YAML config file. If None, uses ~/.config/amplifier-voice/config.yaml
        cli_overrides: Dictionary of CLI argument overrides

    Returns:
        AppConfig instance with merged configuration

    Raises:
        ValueError: If required fields (api_key) are missing
        FileNotFoundError: If specified config_path doesn't exist
    """
    # Start with defaults (from AppConfig dataclass defaults)
    config_dict = {
        "api_key": "",
        "model": "gpt-4o-realtime-preview-2024-12-17",
        "voice": "alloy",
        "temperature": 0.7,
        "max_response_tokens": None,
        "input_device": None,
        "output_device": None,
        "sample_rate": 24000,
        "buffer_size": 1024,
        "max_recording_duration": 30,
        "show_transcripts": True,
        "show_audio_levels": False,
        "show_timestamps": False,
        "theme": "dark",
    }

    # Load from YAML config file if it exists
    if config_path is None:
        config_path = Path.home() / ".config" / "amplifier-voice" / "config.yaml"

    if config_path.exists():
        with open(config_path) as f:
            file_config = yaml.safe_load(f) or {}

        # Merge config sections (YAML has nested structure)
        if "openai" in file_config:
            openai = file_config["openai"]
            if "api_key" in openai:
                config_dict["api_key"] = openai["api_key"]
            if "model" in openai:
                config_dict["model"] = openai["model"]
            if "voice" in openai:
                config_dict["voice"] = openai["voice"]
            if "temperature" in openai:
                config_dict["temperature"] = openai["temperature"]
            if "max_response_tokens" in openai:
                config_dict["max_response_tokens"] = openai["max_response_tokens"]

        if "audio" in file_config:
            audio = file_config["audio"]
            if "input_device" in audio:
                config_dict["input_device"] = audio["input_device"]
            if "output_device" in audio:
                config_dict["output_device"] = audio["output_device"]
            if "sample_rate" in audio:
                config_dict["sample_rate"] = audio["sample_rate"]
            if "buffer_size" in audio:
                config_dict["buffer_size"] = audio["buffer_size"]
            if "max_recording_duration" in audio:
                config_dict["max_recording_duration"] = audio["max_recording_duration"]

        if "ui" in file_config:
            ui = file_config["ui"]
            if "show_transcripts" in ui:
                config_dict["show_transcripts"] = ui["show_transcripts"]
            if "show_audio_levels" in ui:
                config_dict["show_audio_levels"] = ui["show_audio_levels"]
            if "show_timestamps" in ui:
                config_dict["show_timestamps"] = ui["show_timestamps"]
            if "theme" in ui:
                config_dict["theme"] = ui["theme"]

    # Merge environment variables (OPENAI_API_KEY)
    if "OPENAI_API_KEY" in os.environ:
        config_dict["api_key"] = os.environ["OPENAI_API_KEY"]

    # Apply CLI overrides last (highest priority)
    if cli_overrides:
        for key, value in cli_overrides.items():
            if value is not None:  # Only override if CLI value was provided
                config_dict[key] = value

    # Validate required fields
    if not config_dict["api_key"]:
        raise ValueError(
            "OpenAI API key is required. Set OPENAI_API_KEY environment variable, add to config file, or pass --api-key"
        )

    # Handle environment variable substitution in config file
    if config_dict["api_key"].startswith("${") and config_dict["api_key"].endswith("}"):
        env_var = config_dict["api_key"][2:-1]  # Extract variable name
        config_dict["api_key"] = os.environ.get(env_var, "")
        if not config_dict["api_key"]:
            raise ValueError(f"Environment variable {env_var} referenced in config but not set")

    return AppConfig(**config_dict)

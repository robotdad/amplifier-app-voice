"""Amplifier session management for amplifier-app-voice."""

from pathlib import Path

from amplifier_core import AmplifierSession
from amplifier_profiles import ProfileLoader
from amplifier_profiles import compile_profile_to_mount_plan

from .config import AppConfig


class SessionManager:
    """Manages Amplifier session with Realtime provider."""

    def __init__(self, config: AppConfig):
        """
        Initialize session manager with application configuration.

        Args:
            config: Application configuration
        """
        self.config = config
        self.session: AmplifierSession | None = None

    async def create_session(self) -> AmplifierSession:
        """
        Create Amplifier session with OpenAI Realtime provider.

        Loads profile from profiles/voice.md and applies app config overrides.

        Returns:
            Configured AmplifierSession instance

        Raises:
            RuntimeError: If session creation fails
        """
        # Load voice profile from profiles/voice.md
        # Try package directory first (local dev), then installed location (uvx)
        profile_paths = [
            Path(__file__).parent.parent.parent / "profiles",  # Local dev
            Path(__file__).parent.parent / "profiles",  # Also try closer
        ]

        # Add system install location if available
        try:
            import sys
            from pathlib import Path

            site_packages = Path(sys.prefix) / "share" / "amplifier_app_voice" / "profiles"
            if site_packages.exists():
                profile_paths.append(site_packages)
        except Exception:
            pass

        loader = ProfileLoader(search_paths=profile_paths)
        profile = loader.load_profile("voice")

        # Compile to mount plan
        mount_plan = compile_profile_to_mount_plan(profile)

        # Override provider config with app settings
        if mount_plan.get("providers"):
            mount_plan["providers"][0]["config"]["api_key"] = self.config.api_key
            mount_plan["providers"][0]["config"]["model"] = self.config.model
            mount_plan["providers"][0]["config"]["voice"] = self.config.voice
            mount_plan["providers"][0]["config"]["temperature"] = self.config.temperature
            if self.config.max_response_tokens:
                mount_plan["providers"][0]["config"]["max_response_tokens"] = self.config.max_response_tokens

        try:
            self.session = AmplifierSession(config=mount_plan)
            await self.session.__aenter__()
            return self.session
        except Exception as e:
            self.session = None
            raise RuntimeError(f"Failed to create Amplifier session: {e}") from e

    async def close(self):
        """Close session gracefully."""
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
            finally:
                self.session = None

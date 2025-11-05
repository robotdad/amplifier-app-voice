"""Amplifier session management for amplifier-app-voice."""

from amplifier_core import AmplifierSession

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

        Session structure per docs/ARCHITECTURE.md:
        - orchestrator: loop-basic
        - context: context-simple
        - provider: provider-openai-realtime with config settings

        Returns:
            Configured AmplifierSession instance

        Raises:
            RuntimeError: If session creation fails
        """
        session_config = {
            "session": {
                "orchestrator": "loop-basic",
                "context": "context-simple",
            },
            "providers": [
                {
                    "module": "provider-openai-realtime",
                    "source": "git+https://github.com/microsoft/amplifier-module-provider-openai-realtime@main",
                    "config": {
                        "api_key": self.config.api_key,
                        "model": self.config.model,
                        "voice": self.config.voice,
                        "temperature": self.config.temperature,
                    },
                }
            ],
        }

        # Add max_response_tokens if specified
        if self.config.max_response_tokens is not None:
            session_config["providers"][0]["config"]["max_response_tokens"] = self.config.max_response_tokens

        try:
            self.session = AmplifierSession(config=session_config)
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

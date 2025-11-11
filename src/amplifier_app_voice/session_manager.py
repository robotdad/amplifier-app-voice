"""Amplifier session management for amplifier-app-voice."""

import json
import uuid
from datetime import UTC
from datetime import datetime
from pathlib import Path

from amplifier_core import AmplifierSession
from amplifier_profiles import ProfileLoader
from amplifier_profiles import compile_profile_to_mount_plan

from .config import AppConfig


def _get_project_slug() -> str:
    """Generate project slug from CWD (matches hooks-logging)."""
    cwd = Path.cwd().resolve()
    slug = str(cwd).replace("/", "-").replace("\\", "-").replace(":", "")
    if not slug.startswith("-"):
        slug = "-" + slug
    return slug


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
        self.session_id: str | None = None
        self.session_dir: Path | None = None

    async def create_session(self) -> AmplifierSession:
        """
        Create Amplifier session with OpenAI Realtime provider.

        Loads profile from profiles/voice.md and applies app config overrides.

        Returns:
            Configured AmplifierSession instance

        Raises:
            RuntimeError: If session creation fails
        """
        # Generate session ID and setup directory structure
        self.session_id = str(uuid.uuid4())
        project_slug = _get_project_slug()
        self.session_dir = Path.home() / ".amplifier" / "projects" / project_slug / "sessions" / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Create session metadata.json for log viewer
        metadata = {
            "session_id": self.session_id,
            "created_at": datetime.now(UTC).isoformat(),
            "application": "amplifier-app-voice",
            "profile": "voice",
            "model": self.config.model,
            "voice": self.config.voice,
            "temperature": self.config.temperature,
            "project_slug": project_slug,
            "cwd": str(Path.cwd()),
        }
        with (self.session_dir / "metadata.json").open("w") as f:
            json.dump(metadata, f, indent=2)

        # Load voice profile from profiles/voice.md
        # Try package directory first (local dev), then installed location (uvx)
        profile_paths = [
            Path(__file__).parent.parent.parent / "profiles",  # Local dev
            Path(__file__).parent.parent / "profiles",  # Also try closer
        ]

        # Add system install location if available
        try:
            import sys

            site_packages = Path(sys.prefix) / "share" / "amplifier_app_voice" / "profiles"
            if site_packages.exists():
                profile_paths.append(site_packages)
        except Exception:
            pass

        loader = ProfileLoader(search_paths=profile_paths)
        profile = loader.load_profile("voice")

        # Compile to mount plan
        mount_plan = compile_profile_to_mount_plan(profile)

        # Add session_id to mount plan for event tracking
        mount_plan["session_id"] = self.session_id

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
            
            # Emit session:start event
            if self.session and hasattr(self.session, "coordinator") and hasattr(self.session.coordinator, "hooks"):
                await self.session.coordinator.hooks.emit(
                    "session:start",
                    {
                        "session_id": self.session_id,
                        "application": "amplifier-app-voice",
                        "profile": "voice",
                        "model": self.config.model,
                        "voice": self.config.voice,
                    },
                )
            
            return self.session
        except Exception as e:
            self.session = None
            self.session_id = None
            self.session_dir = None
            raise RuntimeError(f"Failed to create Amplifier session: {e}") from e

    async def close(self):
        """Close session gracefully."""
        if self.session:
            try:
                # Emit session:end event
                if hasattr(self.session, "coordinator") and hasattr(self.session.coordinator, "hooks"):
                    await self.session.coordinator.hooks.emit(
                        "session:end",
                        {
                            "session_id": self.session_id,
                            "application": "amplifier-app-voice",
                        },
                    )
                await self.session.__aexit__(None, None, None)
            finally:
                self.session = None
                self.session_id = None
                self.session_dir = None
    
    def write_transcript(self, role: str, content: str, audio_metadata: dict | None = None):
        """Write transcript entry to transcript.jsonl.
        
        Args:
            role: "user" or "assistant"
            content: Transcript text
            audio_metadata: Optional audio metadata (format, sample_rate, duration, etc.)
        """
        if not self.session_dir:
            return
        
        transcript_file = self.session_dir / "transcript.jsonl"
        entry = {
            "ts": datetime.now(UTC).isoformat(),
            "role": role,
            "content": content,
        }
        if audio_metadata:
            entry["audio"] = audio_metadata
        
        try:
            with transcript_file.open("a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            # Don't fail the application if transcript logging fails
            import logging
            logging.error(f"Failed to write transcript: {e}")

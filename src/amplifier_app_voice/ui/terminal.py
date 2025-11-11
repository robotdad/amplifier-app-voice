"""Terminal UI using Rich library for beautiful console output."""

from rich.console import Console
from rich.panel import Panel


class TerminalUI:
    """Terminal UI using Rich library."""

    def __init__(self: "TerminalUI") -> None:
        """Initialize Rich console and transcript storage."""
        self.console = Console()
        self.transcript_lines: list[str] = []

    def show_welcome(self: "TerminalUI") -> None:
        """Display welcome message with instructions."""
        self.console.print(
            Panel(
                "[bold green]Amplifier Voice Assistant[/bold green]\n\n"
                "Press [bold]SPACE[/bold] to start talking\n"
                "Press [bold]SPACE[/bold] again to stop and send\n"
                "Press [bold]Ctrl+C[/bold] to exit",
                title="Welcome",
            )
        )

    def show_status(self: "TerminalUI", message: str, style: str = "") -> None:
        """Display status message with optional styling.

        Args:
            message: Status message to display
            style: Rich style string (e.g., "green", "yellow", "red", "cyan")
        """
        if style:
            self.console.print(f"[{style}]{message}[/{style}]")
        else:
            self.console.print(message)

    def show_transcript(self: "TerminalUI", role: str, text: str) -> None:
        """Display and store conversation transcript entry.

        Args:
            role: Either "user" or "assistant"
            text: Transcript text to display
        """
        prefix = "You:" if role == "user" else "Assistant:"
        line = f"[bold]{prefix}[/bold] {text}"
        self.transcript_lines.append(line)
        self.console.print(line)

    def show_recording(self: "TerminalUI", duration: float) -> None:
        """Display recording status with duration timer.

        Args:
            duration: Recording duration in seconds
        """
        self.console.print(f"[yellow]Recording... ({duration:.1f}s)[/yellow]", end="\r")

    def clear_status(self: "TerminalUI") -> None:
        """Clear the current status line."""
        self.console.print(" " * 80, end="\r")

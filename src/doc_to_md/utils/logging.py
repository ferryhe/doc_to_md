"""Simple logging helper using Rich."""
from __future__ import annotations

from rich.console import Console

console = Console()


def log_info(message: str) -> None:
    console.print(f"[bold green]INFO[/]: {message}")


def log_error(message: str) -> None:
    console.print(f"[bold red]ERROR[/]: {message}")

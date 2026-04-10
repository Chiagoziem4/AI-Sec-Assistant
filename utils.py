"""
Shared utility helpers for ai-sec-assistant.
"""

from __future__ import annotations

import os
import re

from rich.console import Console

console = Console()


def validate_file(file_path: str) -> bool:
    if not os.path.isfile(file_path):
        console.print(f"[bold red]Error:[/bold red] File not found: {file_path}")
        return False
    if os.path.getsize(file_path) == 0:
        console.print(f"[bold red]Error:[/bold red] File is empty: {file_path}")
        return False
    return True


def is_valid_ip(ip: str) -> bool:
    pattern = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
    if not pattern.match(ip):
        return False
    return all(0 <= int(part) <= 255 for part in ip.split("."))


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^\w\-_.]", "_", name)


def print_banner() -> None:
    console.print(
        "\n[bold cyan]"
        "+------------------------------------------+\n"
        "|   AI-Powered Security Assistant v1.0    |\n"
        "+------------------------------------------+"
        "[/bold cyan]\n"
    )

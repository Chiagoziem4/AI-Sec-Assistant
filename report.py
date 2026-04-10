"""
Report generator for CLI and file exports.
"""

from __future__ import annotations

import json
import os
from datetime import datetime

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
OUTPUT_DIR = "outputs"


def ensure_output_dir() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def render_cli(analysis_results: list[dict]) -> None:
    console.print(
        Panel.fit(
            "[bold white]AI-Powered Security Assistant[/bold white]\n[dim]Scan Analysis[/dim]",
            border_style="cyan",
        )
    )

    for host in analysis_results:
        ip = host.get("ip", "unknown")
        hostname = host.get("hostname", "N/A")
        ports = host.get("ports", [])
        analysis = host.get("analysis", "No analysis available.")

        console.print(f"\n[bold cyan]Host: {ip} ({hostname})[/bold cyan]")

        if ports:
            table = Table(
                title="Detected Open Ports",
                box=box.ROUNDED,
                border_style="dim white",
                header_style="bold yellow",
            )
            table.add_column("Port", style="cyan", width=8)
            table.add_column("Proto", width=8)
            table.add_column("State", style="green", width=10)
            table.add_column("Service", style="magenta", width=16)
            table.add_column("Version", width=40)

            for port in ports:
                state = port.get("state", "unknown")
                color = "green" if state == "open" else "red"
                table.add_row(
                    str(port.get("port", "N/A")),
                    str(port.get("protocol", "N/A")),
                    f"[{color}]{state}[/{color}]",
                    str(port.get("service", "N/A")),
                    str(port.get("version", "N/A")),
                )
            console.print(table)
        else:
            console.print("[yellow]No open ports detected.[/yellow]")

        console.print(
            Panel(
                analysis,
                title="[bold red]Security Analysis[/bold red]",
                border_style="red",
                padding=(1, 2),
            )
        )


def save_json(analysis_results: list[dict]) -> str:
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUTPUT_DIR, f"report_{timestamp}.json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(analysis_results, handle, indent=2)
    return path


def save_markdown(analysis_results: list[dict]) -> str:
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUTPUT_DIR, f"report_{timestamp}.md")

    lines = [
        "# AI Security Scan Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    for host in analysis_results:
        lines.append(f"## Host: {host.get('ip')} ({host.get('hostname')})")
        lines.append("")
        lines.append("### Open Ports")
        lines.append("")
        lines.append("| Port | Protocol | State | Service | Version |")
        lines.append("|------|----------|-------|---------|---------|")
        for port in host.get("ports", []):
            lines.append(
                f"| {port.get('port')} | {port.get('protocol')} | {port.get('state')} | "
                f"{port.get('service')} | {port.get('version')} |"
            )
        lines.append("")
        lines.append("### Security Analysis")
        lines.append("")
        lines.append(host.get("analysis", "N/A"))
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    return path


def generate_report(
    analysis_results: list[dict],
    output_json: bool = False,
    output_markdown: bool = False,
) -> None:
    render_cli(analysis_results)

    if output_json:
        path = save_json(analysis_results)
        console.print(f"\n[bold green]JSON report saved:[/bold green] {path}")

    if output_markdown:
        path = save_markdown(analysis_results)
        console.print(f"[bold green]Markdown report saved:[/bold green] {path}")

# AI-Sec Assistant — Complete Build & Usage Guide

> **Version:** 1.0.0 | **Target OS:** Kali Linux / Ubuntu 22.04+ | **Python:** 3.11+

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Requirements](#2-system-requirements)
3. [Environment Setup](#3-environment-setup)
4. [Repository Initialization](#4-repository-initialization)
5. [Project File Structure](#5-project-file-structure)
6. [Installing Dependencies](#6-installing-dependencies)
7. [Writing Each Module](#7-writing-each-module)
   - 7.1 [parser.py — Scan Input Parser](#71-parserpy--scan-input-parser)
   - 7.2 [ai_engine.py — AI Analysis Engine](#72-ai_enginepy--ai-analysis-engine)
   - 7.3 [report.py — Report Generator](#73-reportpy--report-generator)
   - 7.4 [utils.py — Utility Helpers](#74-utilspy--utility-helpers)
   - 7.5 [main.py — CLI Launcher](#75-mainpy--cli-launcher)
8. [Configuration Files](#8-configuration-files)
   - 8.1 [.env — Secrets & Config](#81-env--secrets--config)
   - 8.2 [requirements.txt](#82-requirementstxt)
   - 8.3 [.gitignore](#83-gitignore)
9. [Sample Input Files](#9-sample-input-files)
10. [Running the Tool](#10-running-the-tool)
11. [Testing & Validation](#11-testing--validation)
12. [Optional: Ollama Local LLM Setup](#12-optional-ollama-local-llm-setup)
13. [Optional: Docker Deployment](#13-optional-docker-deployment)
14. [Optional: CVE Lookup Integration](#14-optional-cve-lookup-integration)
15. [Troubleshooting](#15-troubleshooting)
16. [Best Practices & Maintenance](#16-best-practices--maintenance)
17. [Execution Timeline](#17-execution-timeline)

---

## 1. Project Overview

**ai-sec-assistant** is a command-line security intelligence tool that:

- **Ingests** raw scan output from `nmap` or `masscan`
- **Parses** it into structured, normalized JSON
- **Analyzes** each finding using an AI engine (OpenAI API or local Ollama LLM)
- **Outputs** clean, colored CLI reports and optional file exports (JSON / Markdown)

The architecture is intentionally modular — the parser, AI engine, and reporter are decoupled so each can be developed, tested, and swapped independently.

---

## 2. System Requirements

### Hardware (Minimum)

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2-core | 4-core |
| RAM | 4 GB | 8 GB (16 GB for local LLM) |
| Disk | 10 GB free | 20 GB free |

### Operating System

- **Primary:** Kali Linux (rolling release, 2023+)
- **Alternative:** Ubuntu 22.04 LTS or 24.04 LTS

### Required Software

| Software | Minimum Version | Install Command |
|----------|----------------|-----------------|
| Python | 3.11+ | `sudo apt install python3.11` |
| pip | Latest | `python3 -m pip install --upgrade pip` |
| nmap | 7.92+ | `sudo apt install nmap` |
| masscan | 1.0+ | `sudo apt install masscan` |
| git | Any | `sudo apt install git` |
| VS Code | Latest | See note below |

> **VS Code Install (optional but recommended):**
> ```bash
> sudo snap install code --classic
> ```
> Install extensions: `ms-python.python`, `ms-python.vscode-pylance`, `ms-python.black-formatter`, `ms-python.isort`

### Verify Installed Versions

```bash
python3 --version        # Expect: Python 3.11.x or higher
nmap --version           # Expect: Nmap 7.92 or higher
masscan --version        # Expect: 1.0.x
git --version            # Any version
```

---
## 3. Environment Setup

### Step 3.1 — Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 3.2 — Install Python 3.11+ (if not already installed)

```bash
sudo apt install python3.11 python3.11-venv python3.11-dev -y
```

### Step 3.3 — Create Project Directory

```bash
mkdir -p ~/projects/ai-sec-assistant
cd ~/projects/ai-sec-assistant
```

### Step 3.4 — Create and Activate Virtual Environment

```bash
python3.11 -m venv ai-sec-env
source ai-sec-env/bin/activate
```

> **Verify activation:** Your terminal prompt should now show `(ai-sec-env)` as a prefix.

### Step 3.5 — Upgrade pip Inside the Environment

```bash
pip install --upgrade pip setuptools wheel
```

### Step 3.6 — Deactivate / Reactivate (Reference)

```bash
deactivate                        # Exit the virtual environment
source ai-sec-env/bin/activate    # Re-enter the virtual environment
```

---

## 4. Repository Initialization

### Step 4.1 — Initialize Git Repository

```bash
cd ~/projects/ai-sec-assistant
git init
git branch -M main
```

### Step 4.2 — Configure Git Identity (if not already set)

```bash
git config user.name "Your Name"
git config user.email "you@example.com"
```

### Step 4.3 — Create Branch Structure

```bash
git checkout -b dev
git checkout -b feature/parser
git checkout main
```

> **Branch conventions:**
> - `main` — stable, tested code only
> - `dev` — integration branch
> - `feature/*` — individual feature development

### Step 4.4 — Link to Remote (Optional)

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-sec-assistant.git
git push -u origin main
```

---

## 5. Project File Structure

Create all files and directories as shown:

```bash
ai-sec-assistant/
├── main.py               # CLI entry point
├── parser.py             # Scan output parser (nmap / masscan)
├── ai_engine.py          # AI analysis logic (OpenAI or Ollama)
├── report.py             # Output: CLI (Rich) + file (JSON/Markdown)
├── utils.py              # Validation, formatting helpers
├── requirements.txt      # Python dependency list
├── .env                  # API keys and config (never commit)
├── .gitignore            # Exclude secrets and env from git
├── sample_scan.txt       # Sample nmap output for testing
├── sample_masscan.txt    # Sample masscan output for testing
├── tests/
│   ├── test_parser.py    # Unit tests for parser
│   ├── test_ai_engine.py # Unit tests for AI engine
│   └── test_report.py    # Unit tests for reporter
└── outputs/
    └── .gitkeep          # Placeholder — stores generated reports
```

### Create the directory structure:

```bash
mkdir -p tests outputs
touch main.py parser.py ai_engine.py report.py utils.py
touch requirements.txt .env .gitignore sample_scan.txt sample_masscan.txt
touch tests/test_parser.py tests/test_ai_engine.py tests/test_report.py
touch outputs/.gitkeep
```

---
## 6. Installing Dependencies

### Step 6.1 — Install Python Libraries

Ensure your virtual environment is active, then run:

```bash
pip install rich requests openai python-dotenv
```

| Library | Purpose |
|---------|---------|
| `rich` | Colored, formatted terminal output (tables, panels, progress bars) |
| `requests` | HTTP calls for CVE lookups and external AI APIs |
| `openai` | OpenAI GPT API client |
| `python-dotenv` | Load `.env` file into environment variables securely |

### Step 6.2 — Generate requirements.txt

```bash
pip freeze > requirements.txt
```

> This captures exact versions — critical for reproducibility.

### Step 6.3 — Verify Installation

```bash
python3 -c "import rich, requests, openai, dotenv; print('All dependencies OK')"
```

Expected output:
```
All dependencies OK
```

---
## 7. Writing Each Module

### 7.1 `parser.py` — Scan Input Parser

**Purpose:** Read raw nmap or masscan output, extract structured fields, return normalized JSON list.

```python
# parser.py
"""
Parses nmap and masscan scan output into structured JSON.
Supports:
  - nmap default text output (-oN)
  - masscan simple text output
"""

import re
import json
import os

SUPPORTED_FORMATS = ["nmap", "masscan", "auto"]


def detect_format(file_path: str) -> str:
    """
    Auto-detect scan format by reading first few lines.
    Returns: 'nmap' or 'masscan'
    """
    with open(file_path, "r") as f:
        header = f.read(300).lower()
    if "nmap scan report" in header or "nmap" in header:
        return "nmap"
    if "masscan" in header or "rate:" in header:
        return "masscan"
    return "unknown"


def parse_nmap(file_path: str) -> list[dict]:
    """
    Parses nmap text output (-oN format).
    Extracts: ip, hostname, port, protocol, state, service, version.
    """
    results = []
    current_host = {"ip": "unknown", "hostname": "unknown", "ports": []}

    with open(file_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Match host header: "Nmap scan report for hostname (ip)" or "for ip"
        host_match = re.match(
            r"Nmap scan report for (.+?)(?:\s+\((.+?)\))?$", line
        )
        if host_match:
            if current_host["ports"]:
                results.append(current_host)
            hostname_or_ip = host_match.group(1)
            ip = host_match.group(2) or hostname_or_ip
            current_host = {
                "ip": ip,
                "hostname": hostname_or_ip if host_match.group(2) else "N/A",
                "ports": [],
            }
            continue

        # Match port line: "80/tcp   open   http   Apache httpd 2.4.41"
        port_match = re.match(
            r"(\d+)/(tcp|udp)\s+(\w+)\s+(\S+)\s*(.*)", line
        )
        if port_match:
            current_host["ports"].append({
                "port": port_match.group(1),
                "protocol": port_match.group(2),
                "state": port_match.group(3),
                "service": port_match.group(4),
                "version": port_match.group(5).strip() or "N/A",
            })

    # Append last host
    if current_host["ports"]:
        results.append(current_host)

    return results


def parse_masscan(file_path: str) -> list[dict]:
    """
    Parses masscan simple text output.
    Format: "Discovered open port 80/tcp on 192.168.1.1"
    """
    results = {}

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            match = re.match(
                r"Discovered open port (\d+)/(tcp|udp) on ([\d.]+)", line
            )
            if match:
                port = match.group(1)
                proto = match.group(2)
                ip = match.group(3)

                if ip not in results:
                    results[ip] = {"ip": ip, "hostname": "N/A", "ports": []}

                results[ip]["ports"].append({
                    "port": port,
                    "protocol": proto,
                    "state": "open",
                    "service": "unknown",
                    "version": "N/A",
                })

    return list(results.values())


def parse_scan(file_path: str, fmt: str = "auto") -> list[dict]:
    """
    Master parser. Auto-detects or uses specified format.

    Args:
        file_path: Path to scan output file.
        fmt: 'auto', 'nmap', or 'masscan'

    Returns:
        List of host dicts with port details.

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If format is unrecognized.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Scan file not found: {file_path}")

    if fmt == "auto":
        fmt = detect_format(file_path)

    if fmt == "nmap":
        return parse_nmap(file_path)
    elif fmt == "masscan":
        return parse_masscan(file_path)
    else:
        raise ValueError(
            f"Unrecognized scan format: '{fmt}'. Use 'nmap' or 'masscan'."
        )


def to_json(parsed_data: list[dict]) -> str:
    """Serialize parsed results to formatted JSON string."""
    return json.dumps(parsed_data, indent=2)
```

---
### 7.2 `ai_engine.py` — AI Analysis Engine

**Purpose:** Accept parsed JSON data, send it to an AI provider (OpenAI or local Ollama), return actionable security recommendations.

```python
# ai_engine.py
"""
AI Analysis Engine.
Supports:
  - OpenAI GPT-4 / GPT-3.5
  - Ollama (local LLM, e.g., llama3, mistral)
  - Rule-based fallback (no API required)
"""

import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()  # 'openai' or 'ollama'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# ─── Rule-Based Fallback ──────────────────────────────────────────────────────

RULES = {
    "ssh": (
        "SSH is exposed. Verify: (1) Password auth is disabled (use key-based). "
        "(2) Root login is blocked. (3) Version is up to date. "
        "(4) Fail2ban or similar brute-force protection is active."
    ),
    "http": (
        "HTTP (plaintext) is open. Recommend: (1) Redirect all traffic to HTTPS. "
        "(2) Check for directory listing. (3) Review exposed web server version."
    ),
    "https": (
        "HTTPS is open. Verify: (1) TLS version ≥ 1.2 (prefer 1.3). "
        "(2) Certificate is valid and not self-signed. (3) HSTS header is set."
    ),
    "ftp": (
        "FTP is exposed and transmits data in plaintext. "
        "Recommend: Replace with SFTP or FTPS. Disable anonymous login immediately."
    ),
    "telnet": (
        "Telnet is critically insecure — all data including passwords are plaintext. "
        "Disable immediately. Use SSH as replacement."
    ),
    "smb": (
        "SMB is exposed. Risk of EternalBlue and related exploits. "
        "Verify: (1) SMBv1 is disabled. (2) Authentication is required. "
        "(3) Firewall restricts access to trusted hosts only."
    ),
    "rdp": (
        "RDP is exposed. High-value target for brute force and ransomware delivery. "
        "Restrict to VPN or specific IPs. Enable NLA (Network Level Authentication)."
    ),
    "mysql": (
        "MySQL is exposed externally. Database ports should never be internet-facing. "
        "Bind to 127.0.0.1. Use firewall rules to restrict access."
    ),
    "postgresql": (
        "PostgreSQL is exposed externally. Restrict access via pg_hba.conf. "
        "Bind to localhost or trusted network only."
    ),
    "dns": (
        "DNS is exposed. Check: (1) Recursive queries are restricted. "
        "(2) Zone transfers are disabled for untrusted hosts. "
        "(3) DNS amplification is not possible."
    ),
    "smtp": (
        "SMTP is open. Verify: (1) Open relay is disabled. "
        "(2) SPF, DKIM, DMARC records are configured. "
        "(3) Authentication is required for sending."
    ),
}


def rule_based_analysis(port_entry: dict) -> str:
    """
    Lightweight fallback: match service to known risk rules.
    Used when no AI provider is configured or as enrichment.
    """
    service = port_entry.get("service", "").lower()
    for key, advice in RULES.items():
        if key in service:
            return advice
    return (
        f"Service '{service}' on port {port_entry.get('port')} detected. "
        "No specific rule matched. Manually investigate this service."
    )


# ─── OpenAI Analysis ─────────────────────────────────────────────────────────

def analyze_with_openai(host_data: dict) -> str:
    """
    Send a single host's scan data to OpenAI for analysis.
    Returns: AI-generated security analysis string.
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = build_prompt(host_data)

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior penetration tester and security engineer. "
                        "Analyze the provided network scan data. For each open port and service, provide: "
                        "1) Risk level (Critical/High/Medium/Low/Info). "
                        "2) What an attacker could do with this. "
                        "3) Specific, actionable remediation steps. "
                        "Be concise, technical, and structured."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI Error] {str(e)} — falling back to rule-based analysis.\n{rule_based_analysis_host(host_data)}"


# ─── Ollama Local LLM Analysis ───────────────────────────────────────────────

def analyze_with_ollama(host_data: dict) -> str:
    """
    Send host scan data to a local Ollama LLM endpoint.
    Returns: AI-generated security analysis string.
    """
    prompt = build_prompt(host_data)
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": (
            "You are a senior penetration tester. Analyze this scan data. "
            "For each service: state risk level, attack surface, and remediation steps.\n\n"
            + prompt
        ),
        "stream": False,
    }

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate", json=payload, timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "No response from Ollama.")
    except requests.exceptions.ConnectionError:
        return (
            "[Ollama Error] Cannot connect to Ollama. Is it running? "
            f"Expected at {OLLAMA_HOST}\n"
            + rule_based_analysis_host(host_data)
        )
    except Exception as e:
        return f"[Ollama Error] {str(e)}\n" + rule_based_analysis_host(host_data)


# ─── Prompt Builder ──────────────────────────────────────────────────────────

def build_prompt(host_data: dict) -> str:
    """Convert structured host dict into a natural language security prompt."""
    ip = host_data.get("ip", "unknown")
    hostname = host_data.get("hostname", "N/A")
    ports = host_data.get("ports", [])

    lines = [f"Target: {ip} ({hostname})", "Open Ports and Services:"]
    for p in ports:
        lines.append(
            f"  - Port {p['port']}/{p['protocol']} | State: {p['state']} | "
            f"Service: {p['service']} | Version: {p['version']}"
        )

    return "\n".join(lines)


def rule_based_analysis_host(host_data: dict) -> str:
    """Run rule-based analysis on all ports of a host."""
    lines = []
    for p in host_data.get("ports", []):
        lines.append(f"Port {p['port']}: {rule_based_analysis(p)}")
    return "\n".join(lines) if lines else "No open ports found."


# ─── Master Analyzer ─────────────────────────────────────────────────────────

def analyze(parsed_data: list[dict]) -> list[dict]:
    """
    Master analysis function.
    Iterates over all hosts, runs AI or rule-based analysis per host.

    Args:
        parsed_data: Output from parser.parse_scan()

    Returns:
        List of dicts: {ip, hostname, ports, analysis}
    """
    results = []

    for host in parsed_data:
        if AI_PROVIDER == "openai" and OPENAI_API_KEY:
            analysis_text = analyze_with_openai(host)
        elif AI_PROVIDER == "ollama":
            analysis_text = analyze_with_ollama(host)
        else:
            analysis_text = rule_based_analysis_host(host)

        results.append({
            "ip": host.get("ip"),
            "hostname": host.get("hostname"),
            "ports": host.get("ports"),
            "analysis": analysis_text,
        })

    return results
```

---
### 7.3 `report.py` — Report Generator

**Purpose:** Render analysis results as formatted CLI output using Rich, and optionally write to JSON or Markdown files.

```python
# report.py
"""
Report Generator.
Outputs analysis results to:
  - Colored terminal (Rich library)
  - JSON file (outputs/report_<timestamp>.json)
  - Markdown file (outputs/report_<timestamp>.md)
"""

import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()
OUTPUT_DIR = "outputs"


def ensure_output_dir():
    """Create outputs/ directory if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def render_cli(analysis_results: list[dict]):
    """
    Render analysis results as a formatted Rich CLI output.
    """
    console.print(
        Panel.fit(
            "[bold white]AI-Powered Security Assistant[/bold white]\n"
            "[dim]Scan Analysis Report[/dim]",
            border_style="cyan",
        )
    )

    for host in analysis_results:
        ip = host.get("ip", "unknown")
        hostname = host.get("hostname", "N/A")
        ports = host.get("ports", [])
        analysis = host.get("analysis", "No analysis available.")

        # Host header
        console.print(f"\n[bold cyan]━━━ Host: {ip} ({hostname}) ━━━[/bold cyan]")

        # Port table
        if ports:
            table = Table(
                title="Detected Open Ports",
                box=box.ROUNDED,
                border_style="dim white",
                header_style="bold yellow",
            )
            table.add_column("Port", style="cyan", width=10)
            table.add_column("Protocol", width=10)
            table.add_column("State", style="green", width=10)
            table.add_column("Service", style="magenta", width=15)
            table.add_column("Version", width=30)

            for p in ports:
                state_color = "green" if p["state"] == "open" else "red"
                table.add_row(
                    p["port"],
                    p["protocol"],
                    f"[{state_color}]{p['state']}[/{state_color}]",
                    p["service"],
                    p["version"],
                )
            console.print(table)
        else:
            console.print("[yellow]No open ports detected for this host.[/yellow]")

        # AI Analysis panel
        console.print(
            Panel(
                analysis,
                title="[bold red]AI Security Analysis[/bold red]",
                border_style="red",
                padding=(1, 2),
            )
        )


def save_json(analysis_results: list[dict]) -> str:
    """
    Save analysis results to a timestamped JSON file.
    Returns: Path to written file.
    """
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"report_{timestamp}.json")
    with open(filename, "w") as f:
        json.dump(analysis_results, f, indent=2)
    return filename


def save_markdown(analysis_results: list[dict]) -> str:
    """
    Save analysis results to a timestamped Markdown file.
    Returns: Path to written file.
    """
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"report_{timestamp}.md")
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
        for p in host.get("ports", []):
            lines.append(
                f"| {p['port']} | {p['protocol']} | {p['state']} | {p['service']} | {p['version']} |"
            )
        lines.append("")
        lines.append("### AI Security Analysis")
        lines.append("")
        lines.append(host.get("analysis", "N/A"))
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(filename, "w") as f:
        f.write("\n".join(lines))
    return filename


def generate_report(
    analysis_results: list[dict],
    output_json: bool = False,
    output_markdown: bool = False,
):
    """
    Master report function. Always renders CLI output.
    Optionally writes to file based on flags.

    Args:
        analysis_results: Output from ai_engine.analyze()
        output_json: If True, write JSON report to outputs/
        output_markdown: If True, write Markdown report to outputs/
    """
    render_cli(analysis_results)

    if output_json:
        path = save_json(analysis_results)
        console.print(f"\n[bold green]✔ JSON report saved:[/bold green] {path}")

    if output_markdown:
        path = save_markdown(analysis_results)
        console.print(f"[bold green]✔ Markdown report saved:[/bold green] {path}")
```

---

### 7.4 `utils.py` — Utility Helpers

**Purpose:** Input validation, error formatting, and shared helper functions.

```python
# utils.py
"""
Utility functions for ai-sec-assistant.
Includes: file validation, IP validation, safe file naming.
"""

import os
import re
from rich.console import Console

console = Console()


def validate_file(file_path: str) -> bool:
    """
    Check if a file exists and is not empty.
    Returns True if valid, False otherwise.
    """
    if not os.path.isfile(file_path):
        console.print(f"[bold red]Error:[/bold red] File not found: {file_path}")
        return False
    if os.path.getsize(file_path) == 0:
        console.print(f"[bold red]Error:[/bold red] File is empty: {file_path}")
        return False
    return True


def is_valid_ip(ip: str) -> bool:
    """Basic IPv4 validation."""
    pattern = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
    if not pattern.match(ip):
        return False
    parts = ip.split(".")
    return all(0 <= int(p) <= 255 for p in parts)


def sanitize_filename(name: str) -> str:
    """Remove unsafe characters from a filename."""
    return re.sub(r"[^\w\-_.]", "_", name)


def print_banner():
    """Print the tool banner."""
    console.print(
        "\n[bold cyan]"
        "╔══════════════════════════════════════════╗\n"
        "║   AI-Powered Security Assistant v1.0    ║\n"
        "║   github.com/YOUR_USERNAME/ai-sec-tool  ║\n"
        "╚══════════════════════════════════════════╝"
        "[/bold cyan]\n"
    )


def confirm_action(message: str) -> bool:
    """Prompt user for yes/no confirmation."""
    response = input(f"{message} [y/N]: ").strip().lower()
    return response == "y"
```

---
### 7.5 `main.py` — CLI Launcher

**Purpose:** Entry point for the tool. Parses CLI arguments and orchestrates the pipeline.

```python
# main.py
"""
AI-Powered Security Assistant — CLI Entry Point.

Usage:
    python main.py --file sample_scan.txt
    python main.py --file scan.txt --format nmap --json --markdown
    python main.py --file masscan.txt --format masscan --no-ai
"""

import argparse
import sys
from utils import validate_file, print_banner
from parser import parse_scan
from ai_engine import analyze
from report import generate_report


def parse_args():
    parser = argparse.ArgumentParser(
        prog="ai-sec-assistant",
        description="AI-Powered Security Scan Analyzer",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--file", "-f",
        required=True,
        help="Path to scan output file (nmap or masscan)",
    )
    parser.add_argument(
        "--format", "-F",
        choices=["auto", "nmap", "masscan"],
        default="auto",
        help="Scan input format (default: auto-detect)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Export results to JSON file in outputs/",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Export results to Markdown file in outputs/",
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Skip AI analysis; use rule-based analysis only",
    )
    return parser.parse_args()


def main():
    print_banner()
    args = parse_args()

    # Validate input file
    if not validate_file(args.file):
        sys.exit(1)

    # Step 1: Parse scan
    print(f"\n[*] Parsing scan file: {args.file} (format: {args.format})")
    try:
        parsed = parse_scan(args.file, fmt=args.format)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] Parsing failed: {e}")
        sys.exit(1)

    if not parsed:
        print("[WARNING] No hosts or ports found in scan file. Check file content.")
        sys.exit(0)

    print(f"[*] Found {len(parsed)} host(s) with open ports.")

    # Step 2: Analyze
    if args.no_ai:
        print("[*] Running rule-based analysis (--no-ai flag set).")
        import os
        os.environ["AI_PROVIDER"] = "rules"

    print("[*] Running AI analysis...")
    analysis_results = analyze(parsed)

    # Step 3: Generate report
    generate_report(
        analysis_results,
        output_json=args.json,
        output_markdown=args.markdown,
    )


if __name__ == "__main__":
    main()
```

---
## 8. Configuration Files

### 8.1 `.env` — Secrets & Config

```ini
# .env
# ─── AI Provider ───────────────────────────────────────
# Options: 'openai' or 'ollama'
AI_PROVIDER=openai

# ─── OpenAI Settings ───────────────────────────────────
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# ─── Ollama Settings (local LLM) ───────────────────────
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
```

> ⚠️ **Never commit `.env` to version control.** It must be listed in `.gitignore`.

---
### 8.2 `requirements.txt`

```
annotated-types==0.7.0
anyio==4.4.0
certifi==2024.7.4
charset-normalizer==3.3.2
distro==1.9.0
h11==0.14.0
httpcore==1.0.5
httpx==0.27.0
idna==3.7
markdown-it-py==3.0.0
mdurl==0.1.3
openai==1.40.0
python-dotenv==1.0.1
requests==2.32.3
rich==13.7.1
sniffio==1.3.1
tqdm==4.66.4
urllib3==2.2.2
```

> Generate the exact version list for your environment with: `pip freeze > requirements.txt`

---
### 8.3 `.gitignore`

```gitignore
# Python environment
ai-sec-env/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Secrets — NEVER commit
.env

# Outputs — local only
outputs/
!outputs/.gitkeep

# IDE
.vscode/
.idea/

# OS artifacts
.DS_Store
Thumbs.db

# Distribution
dist/
build/
*.egg-info/
```

---
## 9. Sample Input Files

### `sample_scan.txt` — nmap Sample

```
# Nmap 7.94 scan initiated Mon Jan  1 12:00:00 2024
Nmap scan report for 192.168.1.1
Host is up (0.0010s latency).

PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.5
80/tcp   open  http        Apache httpd 2.4.41
443/tcp  open  https       Apache httpd 2.4.41
3306/tcp open  mysql       MySQL 5.7.38

Nmap scan report for 192.168.1.100
Host is up (0.0020s latency).

PORT    STATE SERVICE VERSION
21/tcp  open  ftp     vsftpd 3.0.3
23/tcp  open  telnet  Linux telnetd
445/tcp open  smb     Samba smbd 4.0

# Nmap done: 2 IP addresses (2 hosts up) scanned
```

### `sample_masscan.txt` — masscan Sample

```
# masscan 1.0.5
Discovered open port 80/tcp on 10.0.0.1
Discovered open port 443/tcp on 10.0.0.1
Discovered open port 22/tcp on 10.0.0.2
Discovered open port 3389/tcp on 10.0.0.3
```

---
## 10. Running the Tool

### Step 10.1 — Activate the Virtual Environment

```bash
cd ~/projects/ai-sec-assistant
source ai-sec-env/bin/activate
```

### Step 10.2 — Basic Usage (Auto-detect Format)

```bash
python main.py --file sample_scan.txt
```

### Step 10.3 — Specify Format Explicitly

```bash
python main.py --file sample_scan.txt --format nmap
python main.py --file sample_masscan.txt --format masscan
```

### Step 10.4 — Export Reports to Files

```bash
# Export to JSON only
python main.py --file sample_scan.txt --json

# Export to Markdown only
python main.py --file sample_scan.txt --markdown

# Export to both
python main.py --file sample_scan.txt --json --markdown
```

### Step 10.5 — Run Without AI (Rule-Based Only)

```bash
python main.py --file sample_scan.txt --no-ai
```

### Step 10.6 — Run a Live nmap Scan and Pipe Directly

```bash
# Run nmap and save output
sudo nmap -sV -oN live_scan.txt 192.168.1.0/24

# Immediately analyze
python main.py --file live_scan.txt --format nmap --json --markdown
```

### Step 10.7 — Full Example Output (CLI)

```
╔══════════════════════════════════════════╗
║   AI-Powered Security Assistant v1.0    ║
╚══════════════════════════════════════════╝

[*] Parsing scan file: sample_scan.txt (format: auto)
[*] Found 2 host(s) with open ports.
[*] Running AI analysis...

━━━ Host: 192.168.1.1 (N/A) ━━━

┌─────────────────────────────────────────────────────┐
│           Detected Open Ports                       │
├──────┬──────────┬───────┬─────────┬─────────────────┤
│ Port │ Protocol │ State │ Service │ Version         │
├──────┼──────────┼───────┼─────────┼─────────────────┤
│ 22   │ tcp      │ open  │ ssh     │ OpenSSH 8.2p1   │
│ 80   │ tcp      │ open  │ http    │ Apache 2.4.41   │
│ 443  │ tcp      │ open  │ https   │ Apache 2.4.41   │
│ 3306 │ tcp      │ open  │ mysql   │ MySQL 5.7.38    │
└──────┴──────────┴───────┴─────────┴─────────────────┘

╔══════════════════════════════════════════╗
║         AI Security Analysis            ║
╠══════════════════════════════════════════╣
║ Port 22 (SSH): MEDIUM risk...           ║
║ Port 80 (HTTP): HIGH risk...            ║
║ Port 3306 (MySQL): CRITICAL risk...     ║
╚══════════════════════════════════════════╝

✔ JSON report saved: outputs/report_20240101_120000.json
✔ Markdown report saved: outputs/report_20240101_120000.md
```

---
## 11. Testing & Validation

### Step 11.1 — Unit Test: Parser

```python
# tests/test_parser.py
import unittest
import os
import tempfile
from parser import parse_scan, detect_format


class TestParser(unittest.TestCase):

    def setUp(self):
        self.nmap_sample = """Nmap scan report for 192.168.1.1
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2
80/tcp open  http    Apache 2.4.41
"""
        self.masscan_sample = (
            "Discovered open port 80/tcp on 10.0.0.1\n"
            "Discovered open port 22/tcp on 10.0.0.2\n"
        )

    def write_temp(self, content):
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        tmp.write(content)
        tmp.close()
        return tmp.name

    def test_nmap_parsing(self):
        path = self.write_temp(self.nmap_sample)
        result = parse_scan(path, fmt="nmap")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["ip"], "192.168.1.1")
        self.assertEqual(len(result[0]["ports"]), 2)
        self.assertEqual(result[0]["ports"][0]["port"], "22")
        os.unlink(path)

    def test_masscan_parsing(self):
        path = self.write_temp(self.masscan_sample)
        result = parse_scan(path, fmt="masscan")
        self.assertEqual(len(result), 2)
        os.unlink(path)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            parse_scan("/nonexistent/path.txt")

    def test_auto_detect_nmap(self):
        path = self.write_temp(self.nmap_sample)
        fmt = detect_format(path)
        self.assertEqual(fmt, "nmap")
        os.unlink(path)


if __name__ == "__main__":
    unittest.main()
```

### Step 11.2 — Run All Tests

```bash
python -m pytest tests/ -v
```

Expected output:

```
tests/test_parser.py::TestParser::test_auto_detect_nmap PASSED
tests/test_parser.py::TestParser::test_file_not_found PASSED
tests/test_parser.py::TestParser::test_masscan_parsing PASSED
tests/test_parser.py::TestParser::test_nmap_parsing PASSED
4 passed in 0.32s
```

### Step 11.3 — Validate a Full Pipeline Run

```bash
python main.py --file sample_scan.txt --no-ai --json
```

Then verify:

```bash
ls outputs/
cat outputs/report_*.json | python3 -m json.tool
```

---
## 12. Optional: Ollama Local LLM Setup

Use this if you want fully offline, private AI analysis without an OpenAI API key.

### Step 12.1 — Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 12.2 — Pull a Model

```bash
ollama pull llama3      # ~4GB, recommended
# OR
ollama pull mistral     # ~4GB, alternative
```

### Step 12.3 — Start Ollama Server

```bash
ollama serve
```

> Ollama runs at `http://localhost:11434` by default.

### Step 12.4 — Configure `.env`

```ini
AI_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
```

### Step 12.5 — Test Ollama Connection

```bash
curl http://localhost:11434/api/generate \
  -d '{"model":"llama3","prompt":"Hello","stream":false}'
```

Expected: JSON response with a `"response"` field.

### Step 12.6 — Run Tool With Ollama

```bash
python main.py --file sample_scan.txt --format nmap
```

---
## 13. Optional: Docker Deployment

### Step 13.1 — Create `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y nmap && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default entry point
ENTRYPOINT ["python", "main.py"]
```

### Step 13.2 — Create `.dockerignore`

```
ai-sec-env/
.env
outputs/
__pycache__/
*.pyc
.git/
```

### Step 13.3 — Build Docker Image

```bash
docker build -t ai-sec-assistant:1.0 .
```

### Step 13.4 — Run in Docker

```bash
docker run --rm \
  -v $(pwd)/sample_scan.txt:/app/sample_scan.txt \
  -v $(pwd)/outputs:/app/outputs \
  --env-file .env \
  ai-sec-assistant:1.0 \
  --file sample_scan.txt --json --markdown
```

---
## 14. Optional: CVE Lookup Integration

Add CVE enrichment to `ai_engine.py` using the public NVD API:

```python
# Add to ai_engine.py

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

def lookup_cve(keyword: str) -> list[dict]:
    """
    Search NVD for CVEs matching a service/version keyword.
    Returns top 3 CVEs with ID, description, and severity.
    """
    try:
        response = requests.get(
            NVD_API_URL,
            params={"keywordSearch": keyword, "resultsPerPage": 3},
            timeout=10,
        )
        response.raise_for_status()
        items = response.json().get("vulnerabilities", [])
        cves = []
        for item in items:
            cve = item.get("cve", {})
            cves.append({
                "id": cve.get("id"),
                "description": cve.get("descriptions", [{}])[0].get("value", "N/A"),
                "severity": cve.get("metrics", {})
                    .get("cvssMetricV31", [{}])[0]
                    .get("cvssData", {})
                    .get("baseSeverity", "N/A"),
            })
        return cves
    except Exception:
        return []
```

Call `lookup_cve(service_name)` inside `analyze()` and append results to each port's analysis.

---
## 15. Troubleshooting

### ❌ `ModuleNotFoundError: No module named 'rich'`

**Cause:** Virtual environment is not activated.

```bash
source ai-sec-env/bin/activate
pip install rich
```

---
### ❌ `FileNotFoundError: Scan file not found`

**Cause:** Incorrect file path passed to `--file`.

```bash
ls -la sample_scan.txt    # Confirm file exists
python main.py --file ./sample_scan.txt
```

---
### ❌ `openai.AuthenticationError: Invalid API key`

**Cause:** `OPENAI_API_KEY` in `.env` is missing, expired, or incorrect.

```bash
cat .env | grep OPENAI_API_KEY    # Check key is present
```

Get a valid key at: https://platform.openai.com/api-keys

---
### ❌ `ConnectionError: Cannot connect to Ollama`

**Cause:** Ollama server is not running.

```bash
ollama serve &            # Start in background
curl http://localhost:11434   # Test connection
```

---
### ❌ `ValueError: Unrecognized scan format`

**Cause:** The auto-detector could not identify the format.

```bash
python main.py --file scan.txt --format nmap    # Force format explicitly
```

---
### ❌ `No hosts or ports found in scan file`

**Cause:** File is valid but contains no parseable data (e.g., all hosts down, wrong nmap flags used).

```bash
# Ensure nmap was run with -sV for service detection:
sudo nmap -sV -oN scan.txt 192.168.1.1

# Check file has port lines
grep "open" scan.txt
```

---
### ❌ Parser returns empty list for nmap output

**Cause:** Nmap was run without `-oN` (normal text output). XML or grepable formats differ.

```bash
# Always use -oN for this tool's parser:
sudo nmap -sV -oN scan.txt TARGET_IP
```

---
### ❌ pip install fails with permission error

**Cause:** Installing outside virtual environment.

```bash
source ai-sec-env/bin/activate
pip install -r requirements.txt
```

---
## 16. Best Practices & Maintenance

### Security

- Always store secrets in `.env` and confirm `.env` is in `.gitignore` before first commit
- Run `git status` before every `git push` to verify no sensitive files are staged
- Rotate OpenAI API keys periodically at https://platform.openai.com/api-keys

### Code Quality

- Run `black .` before committing to enforce PEP 8 formatting
- Use `isort .` to sort imports consistently
- Run `python -m pytest tests/ -v` before every merge to `main`

### Version Control Workflow

```bash
# Start a new feature
git checkout dev
git checkout -b feature/cve-lookup

# After development
git add .
git commit -m "feat: add NVD CVE lookup integration"
git checkout dev
git merge feature/cve-lookup

# Promote to main after testing
git checkout main
git merge dev
git tag v1.1.0
git push origin main --tags
```

### Keeping Dependencies Updated

```bash
pip list --outdated
pip install --upgrade rich openai requests python-dotenv
pip freeze > requirements.txt
```

---
## 17. Execution Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Environment & Repo Setup | 1 day | Python env active, Git initialized, all files created |
| Parser Module (`parser.py`) | 1–2 days | Correctly parses nmap and masscan formats |
| AI Engine Prototype (`ai_engine.py`) | 2 days | Rule-based fallback working; OpenAI integration tested |
| Reporting (`report.py`) | 1 day | Rich CLI output + JSON/Markdown export working |
| CLI Entry Point (`main.py`) | 0.5 days | Flags wired, pipeline end-to-end functional |
| Testing & Edge Cases | 2–3 days | Unit tests passing; tested on real scan files |
| Ollama Integration | 1–2 days | Local LLM operational offline |
| CVE Lookup | 1 day | NVD API integrated per port |
| Docker Container | 1 day | Image builds cleanly, runs portably |
| Documentation & README Polish | 1 day | README finalized, usage examples verified |

---
## Quick Reference Card

```bash
# Setup (first time only)
python3.11 -m venv ai-sec-env && source ai-sec-env/bin/activate
pip install -r requirements.txt

# Run (every session)
source ai-sec-env/bin/activate
python main.py --file sample_scan.txt --json --markdown

# Test
python -m pytest tests/ -v

# Live scan + analyze
sudo nmap -sV -oN live.txt 192.168.1.0/24
python main.py --file live.txt --json

# Check outputs
ls outputs/
```

---
*Built with Python 3.11 · Rich · OpenAI / Ollama · nmap / masscan*

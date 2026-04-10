"""
AI-Powered Security Assistant - CLI Entry Point.
"""

from __future__ import annotations

import argparse
import getpass
import os
import sys
from parser import parse_scan

from ai_engine import analyze, build_runtime_config, validate_runtime_ai_setup
from report import generate_report
from utils import print_banner, validate_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ai-sec-assistant",
        description="AI-Powered Security Scan Analyzer",
    )
    parser.add_argument(
        "--file",
        "-f",
        required=True,
        help="Path to scan output file (nmap or masscan)",
    )
    parser.add_argument(
        "--format",
        "-F",
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
        help="Skip AI analysis and use rule-based analysis only",
    )
    return parser.parse_args()


def prompt_provider_choice() -> str:
    print("\n[?] Select analysis mode before continuing:")
    print("    1) OpenAI API")
    print("    2) Local LLM (Ollama)")
    print("    3) Rule-based only (no AI)")
    while True:
        choice = input("Enter choice [1/2/3]: ").strip()
        if choice == "1":
            return "openai"
        if choice == "2":
            return "ollama"
        if choice == "3":
            return "rules"
        print("[ERROR] Invalid choice. Please enter 1, 2, or 3.")


def ensure_openai_key() -> None:
    if os.getenv("OPENAI_API_KEY"):
        return
    print("\n[!] OPENAI_API_KEY is not set.")
    api_key = getpass.getpass("Enter OpenAI API key (input hidden): ").strip()
    if not api_key:
        print("[ERROR] API key is required for OpenAI mode.")
        sys.exit(1)
    os.environ["OPENAI_API_KEY"] = api_key


def resolve_provider(no_ai: bool) -> str:
    if no_ai:
        return "rules"

    selected = prompt_provider_choice()
    if selected == "openai":
        ensure_openai_key()
    os.environ["AI_PROVIDER"] = selected
    return selected


def main() -> None:
    print_banner()
    args = parse_args()

    if not validate_file(args.file):
        sys.exit(1)

    print(f"\n[*] Parsing scan file: {args.file} (format: {args.format})")
    try:
        parsed = parse_scan(args.file, fmt=args.format)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] Parsing failed: {exc}")
        sys.exit(1)

    if not parsed:
        print("[WARNING] No hosts or ports found in scan file. Check file content.")
        sys.exit(0)

    print(f"[*] Found {len(parsed)} host(s) with open ports.")

    provider = resolve_provider(args.no_ai)
    config = build_runtime_config(provider_override=provider)
    ok, message = validate_runtime_ai_setup(config)
    if not ok:
        print(f"[ERROR] {message}")
        sys.exit(1)

    print(f"[*] Running analysis with provider: {config.provider}")
    analysis_results = analyze(parsed, config=config)

    generate_report(
        analysis_results=analysis_results,
        output_json=args.json,
        output_markdown=args.markdown,
    )


if __name__ == "__main__":
    main()

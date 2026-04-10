"""
AI Analysis Engine.
Supports OpenAI, Ollama, and rule-based fallback.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


@dataclass(frozen=True)
class RuntimeConfig:
    provider: str
    openai_api_key: str
    openai_model: str
    ollama_host: str
    ollama_model: str


RULES = {
    "ssh": (
        "SSH exposed. Verify key-only auth, disable root login, patch OpenSSH, and "
        "enforce brute-force controls."
    ),
    "http": (
        "HTTP exposed. Enforce HTTPS redirect, review server banners, and test for "
        "common web misconfigurations."
    ),
    "https": (
        "HTTPS exposed. Validate certificate, disable weak ciphers, and enforce TLS 1.2+."
    ),
    "ftp": (
        "FTP exposed in plaintext. Replace with SFTP/FTPS and disable anonymous access."
    ),
    "telnet": ("Telnet exposed and insecure. Disable immediately and migrate to SSH."),
    "smb": (
        "SMB exposed. Ensure SMBv1 is disabled, patch aggressively, and restrict by IP."
    ),
    "rdp": (
        "RDP exposed. Restrict to VPN/trusted IPs, enable NLA, and enforce MFA where possible."
    ),
    "mysql": (
        "MySQL exposed externally. Restrict network access and avoid internet-facing DB ports."
    ),
    "postgresql": (
        "PostgreSQL exposed externally. Restrict via pg_hba.conf and firewall rules."
    ),
    "dns": ("DNS exposed. Confirm recursion and zone transfers are locked down."),
    "smtp": ("SMTP exposed. Validate relay controls and enforce SPF/DKIM/DMARC."),
}


def build_runtime_config(provider_override: str | None = None) -> RuntimeConfig:
    """
    Read runtime configuration from environment.
    """
    provider = (provider_override or os.getenv("AI_PROVIDER", "openai")).strip().lower()
    return RuntimeConfig(
        provider=provider,
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip(),
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434").strip(),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3").strip(),
    )


def validate_runtime_ai_setup(config: RuntimeConfig) -> tuple[bool, str]:
    """
    Validate provider setup before analysis starts.
    """
    if config.provider == "rules":
        return True, "Rule-based mode selected."

    if config.provider == "openai":
        if not config.openai_api_key:
            return False, "OpenAI mode requires OPENAI_API_KEY."
        return True, "OpenAI configuration is ready."

    if config.provider == "ollama":
        try:
            response = requests.get(f"{config.ollama_host}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            names = {item.get("name", "").split(":")[0] for item in models}
            if config.ollama_model not in names:
                return (
                    False,
                    f"Ollama model '{config.ollama_model}' not found on {config.ollama_host}.",
                )
            return True, "Ollama configuration is ready."
        except requests.RequestException as exc:
            return False, f"Cannot connect to Ollama at {config.ollama_host}: {exc}"

    return False, f"Unsupported AI_PROVIDER: {config.provider}"


def rule_based_analysis(port_entry: dict) -> str:
    """
    Lightweight fallback for service-based advice.
    """
    service = (port_entry.get("service") or "").strip().lower()

    # Exact service name match first.
    if service in RULES:
        return RULES[service]

    # Then partial matches, longest key first to avoid "http" beating "https".
    for key in sorted(RULES.keys(), key=len, reverse=True):
        if key in service:
            return RULES[key]
    return (
        f"Service '{service or 'unknown'}' on port {port_entry.get('port')} detected. "
        "No specific rule matched; perform manual review."
    )


def rule_based_analysis_host(host_data: dict) -> str:
    """
    Aggregate rule-based advice for a full host.
    """
    lines = []
    for port in host_data.get("ports", []):
        lines.append(f"Port {port.get('port')}: {rule_based_analysis(port)}")
    return "\n".join(lines) if lines else "No open ports found."


def build_prompt(host_data: dict) -> str:
    """
    Convert host data into a structured prompt.
    """
    ip = host_data.get("ip", "unknown")
    hostname = host_data.get("hostname", "N/A")
    ports = host_data.get("ports", [])

    lines = [f"Target: {ip} ({hostname})", "Open Ports and Services:"]
    for port in ports:
        lines.append(
            f"- {port.get('port')}/{port.get('protocol')} | state={port.get('state')} "
            f"| service={port.get('service')} | version={port.get('version')}"
        )

    return "\n".join(lines)


def analyze_with_openai(host_data: dict, config: RuntimeConfig) -> str:
    """
    Analyze one host with OpenAI.
    """
    client = OpenAI(api_key=config.openai_api_key)
    prompt = build_prompt(host_data)
    try:
        response = client.chat.completions.create(
            model=config.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior penetration tester. For each open service, provide "
                        "risk level, realistic attacker impact, and concrete remediation steps."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=900,
        )
        content = response.choices[0].message.content
        return content.strip() if content else "No content returned by OpenAI."
    except Exception as exc:
        return (
            f"[OpenAI Error] {exc}\n"
            "Falling back to rule-based analysis:\n"
            f"{rule_based_analysis_host(host_data)}"
        )


def analyze_with_ollama(host_data: dict, config: RuntimeConfig) -> str:
    """
    Analyze one host with a local Ollama model.
    """
    prompt = build_prompt(host_data)
    payload = {
        "model": config.ollama_model,
        "prompt": (
            "You are a senior penetration tester. For each open service, provide risk level, "
            "attacker impact, and concrete remediation.\n\n" + prompt
        ),
        "stream": False,
    }
    try:
        response = requests.post(
            f"{config.ollama_host}/api/generate",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.json().get("response", "No response content from Ollama.")
    except requests.RequestException as exc:
        return (
            f"[Ollama Error] {exc}\n"
            "Falling back to rule-based analysis:\n"
            f"{rule_based_analysis_host(host_data)}"
        )


def analyze(parsed_data: list[dict], config: RuntimeConfig | None = None) -> list[dict]:
    """
    Analyze parsed scan output host-by-host.
    """
    runtime = config or build_runtime_config()
    results: list[dict] = []

    for host in parsed_data:
        if runtime.provider == "openai":
            analysis_text = analyze_with_openai(host, runtime)
        elif runtime.provider == "ollama":
            analysis_text = analyze_with_ollama(host, runtime)
        else:
            analysis_text = rule_based_analysis_host(host)

        results.append(
            {
                "ip": host.get("ip"),
                "hostname": host.get("hostname"),
                "ports": host.get("ports", []),
                "analysis": analysis_text,
            }
        )

    return results


def serialize_analysis(analysis_results: list[dict]) -> str:
    """
    Helper for tests/debugging.
    """
    return json.dumps(analysis_results, indent=2)

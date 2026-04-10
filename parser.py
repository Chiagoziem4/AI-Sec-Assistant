"""
Parses nmap and masscan scan output into structured JSON.
"""

from __future__ import annotations

import json
import os
import re

SUPPORTED_FORMATS = ["nmap", "masscan", "auto"]


def detect_format(file_path: str) -> str:
    """
    Auto-detect scan format by reading the header.
    Returns: 'nmap', 'masscan', or 'unknown'
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
        header = handle.read(500).lower()

    if "nmap scan report" in header or "# nmap" in header:
        return "nmap"
    if "masscan" in header or "discovered open port" in header:
        return "masscan"
    return "unknown"


def parse_nmap(file_path: str) -> list[dict]:
    """
    Parse nmap -oN output.
    """
    results: list[dict] = []
    current_host: dict | None = None

    with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
        lines = handle.readlines()

    for raw_line in lines:
        line = raw_line.strip()

        host_match = re.match(r"Nmap scan report for (.+?)(?:\s+\((.+?)\))?$", line)
        if host_match:
            if current_host and current_host["ports"]:
                results.append(current_host)

            hostname_or_ip = host_match.group(1)
            ip = host_match.group(2) or hostname_or_ip
            hostname = hostname_or_ip if host_match.group(2) else "N/A"
            current_host = {"ip": ip, "hostname": hostname, "ports": []}
            continue

        if not current_host:
            continue

        port_match = re.match(r"(\d+)/(tcp|udp)\s+(\w+)\s+(\S+)\s*(.*)", line)
        if port_match:
            current_host["ports"].append(
                {
                    "port": port_match.group(1),
                    "protocol": port_match.group(2),
                    "state": port_match.group(3),
                    "service": port_match.group(4),
                    "version": port_match.group(5).strip() or "N/A",
                }
            )

    if current_host and current_host["ports"]:
        results.append(current_host)

    return results


def parse_masscan(file_path: str) -> list[dict]:
    """
    Parse masscan simple text output.
    """
    by_host: dict[str, dict] = {}

    with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            match = re.match(r"Discovered open port (\d+)/(tcp|udp) on ([\d.]+)", line)
            if not match:
                continue

            port = match.group(1)
            proto = match.group(2)
            ip = match.group(3)

            if ip not in by_host:
                by_host[ip] = {"ip": ip, "hostname": "N/A", "ports": []}

            by_host[ip]["ports"].append(
                {
                    "port": port,
                    "protocol": proto,
                    "state": "open",
                    "service": "unknown",
                    "version": "N/A",
                }
            )

    return list(by_host.values())


def parse_scan(file_path: str, fmt: str = "auto") -> list[dict]:
    """
    Master parser.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Scan file not found: {file_path}")

    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unrecognized scan format: '{fmt}'. Use nmap, masscan, or auto."
        )

    detected = detect_format(file_path) if fmt == "auto" else fmt
    if detected == "nmap":
        return parse_nmap(file_path)
    if detected == "masscan":
        return parse_masscan(file_path)

    raise ValueError(
        "Unrecognized scan format after detection. Try --format nmap or --format masscan."
    )


def to_json(parsed_data: list[dict]) -> str:
    """
    Serialize parsed results to JSON string.
    """
    return json.dumps(parsed_data, indent=2)

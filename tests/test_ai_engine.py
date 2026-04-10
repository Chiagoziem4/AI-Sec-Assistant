from unittest.mock import patch

from ai_engine import (
    RuntimeConfig,
    analyze,
    rule_based_analysis,
    validate_runtime_ai_setup,
)


def test_rule_based_analysis_known_service() -> None:
    text = rule_based_analysis({"service": "ssh", "port": "22"})
    assert "SSH" in text


def test_rule_based_analysis_https_not_http() -> None:
    text = rule_based_analysis({"service": "https", "port": "443"})
    assert "TLS" in text


def test_validate_openai_requires_key() -> None:
    config = RuntimeConfig(
        provider="openai",
        openai_api_key="",
        openai_model="gpt-4o-mini",
        ollama_host="http://localhost:11434",
        ollama_model="llama3",
    )
    ok, message = validate_runtime_ai_setup(config)
    assert ok is False
    assert "OPENAI_API_KEY" in message


@patch("ai_engine.requests.get")
def test_validate_ollama_model_missing(mock_get) -> None:
    mock_get.return_value.json.return_value = {"models": [{"name": "mistral:latest"}]}
    mock_get.return_value.raise_for_status.return_value = None
    config = RuntimeConfig(
        provider="ollama",
        openai_api_key="",
        openai_model="gpt-4o-mini",
        ollama_host="http://localhost:11434",
        ollama_model="llama3",
    )
    ok, message = validate_runtime_ai_setup(config)
    assert ok is False
    assert "not found" in message


def test_analyze_rules_mode() -> None:
    parsed = [
        {
            "ip": "192.168.1.1",
            "hostname": "N/A",
            "ports": [
                {
                    "port": "22",
                    "protocol": "tcp",
                    "state": "open",
                    "service": "ssh",
                    "version": "OpenSSH",
                }
            ],
        }
    ]
    config = RuntimeConfig(
        provider="rules",
        openai_api_key="",
        openai_model="gpt-4o-mini",
        ollama_host="http://localhost:11434",
        ollama_model="llama3",
    )
    result = analyze(parsed, config=config)
    assert len(result) == 1
    assert "analysis" in result[0]

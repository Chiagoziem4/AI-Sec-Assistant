import os

from report import save_json, save_markdown


def test_save_json(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    payload = [{"ip": "1.1.1.1", "hostname": "N/A", "ports": [], "analysis": "ok"}]
    path = save_json(payload)
    assert os.path.exists(path)
    assert path.endswith(".json")


def test_save_markdown(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    payload = [{"ip": "1.1.1.1", "hostname": "N/A", "ports": [], "analysis": "ok"}]
    path = save_markdown(payload)
    assert os.path.exists(path)
    assert path.endswith(".md")

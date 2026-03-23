from pathlib import Path
import sys

from fastapi.testclient import TestClient
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


client = TestClient(main.app)


def test_health_smoke() -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["agent"] == "text_summarizer"


def test_summarize_smoke(monkeypatch) -> None:
    async def fake_run_agent_prompt(prompt: str, user_id: str) -> str:
        assert prompt
        assert user_id
        return "A concise summary for smoke testing."

    monkeypatch.setattr(main, "run_agent_prompt", fake_run_agent_prompt)

    response = client.post(
        "/summarize",
        json={"input": "Long text to summarize.", "user_id": "tester"},
    )
    assert response.status_code == 200
    assert response.json() == {"summary": "A concise summary for smoke testing."}


def test_structured_smoke(monkeypatch) -> None:
    async def fake_run_agent_prompt(prompt: str, user_id: str) -> str:
        assert "ONLY valid JSON" in prompt
        assert user_id == "tester"
        return '{"title":"AI Impact","bullets":["Transforms operations","Improves decisions","Creates new capabilities"]}'

    monkeypatch.setattr(main, "run_agent_prompt", fake_run_agent_prompt)

    response = client.post(
        "/summarize/structured",
        json={"input": "Long text to summarize.", "user_id": "tester"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "AI Impact"
    assert len(data["bullets"]) == 3


@pytest.mark.parametrize("bullet_count", [3, 5])
def test_structured_contract_accepts_3_to_5_bullets(monkeypatch, bullet_count: int) -> None:
    async def fake_run_agent_prompt(prompt: str, user_id: str) -> str:
        bullets = [f"Point {i}" for i in range(1, bullet_count + 1)]
        bullet_json = ",".join([f'\"{item}\"' for item in bullets])
        return f'{{"title":"Contract OK","bullets":[{bullet_json}]}}'

    monkeypatch.setattr(main, "run_agent_prompt", fake_run_agent_prompt)

    response = client.post(
        "/summarize/structured",
        json={"input": "Contract text.", "user_id": "tester"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Contract OK"
    assert len(data["bullets"]) == bullet_count


@pytest.mark.parametrize("bullet_count", [2, 6])
def test_structured_contract_rejects_outside_3_to_5(monkeypatch, bullet_count: int) -> None:
    async def fake_run_agent_prompt(prompt: str, user_id: str) -> str:
        bullets = [f"Point {i}" for i in range(1, bullet_count + 1)]
        bullet_json = ",".join([f'\"{item}\"' for item in bullets])
        return f'{{"title":"Contract Fail","bullets":[{bullet_json}]}}'

    monkeypatch.setattr(main, "run_agent_prompt", fake_run_agent_prompt)

    response = client.post(
        "/summarize/structured",
        json={"input": "Contract text.", "user_id": "tester"},
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Structured output must contain 3-5 bullets"

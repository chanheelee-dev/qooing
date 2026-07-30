import json
from pathlib import Path

from app.main import create_app
from fastapi.testclient import TestClient


def write_wiki(root: Path) -> None:
    root.mkdir(parents=True)
    (root / "newborn-sleep.md").write_text(
        "---\ntype: Wiki\ntitle: 신생아 수면 기초\n"
        "description: 개발 흐름을 확인하기 위한 예시 문서\n"
        "sources: [/references/example-guidance.md]\n---\n# 수면\n",
        encoding="utf-8",
    )


def client(tmp_path: Path) -> TestClient:
    wiki_root = tmp_path / "wiki"
    write_wiki(wiki_root)
    return TestClient(create_app(wiki_root=wiki_root, model_name=None))


def parse_sse(text: str) -> list[tuple[str, dict[str, str]]]:
    events = []
    for block in text.strip().split("\n\n"):
        lines = block.splitlines()
        event = lines[0].removeprefix("event: ")
        data = json.loads(lines[1].removeprefix("data: "))
        events.append((event, data))
    return events


def test_health_reports_offline_mode(tmp_path: Path) -> None:
    response = client(tmp_path).get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "chat_mode": "offline"}


def test_wiki_routes_list_and_read_documents(tmp_path: Path) -> None:
    api = client(tmp_path)

    listing = api.get("/api/wiki")
    document = api.get("/api/wiki/newborn-sleep")

    assert listing.json() == [
        {
            "slug": "newborn-sleep",
            "title": "신생아 수면 기초",
            "description": "개발 흐름을 확인하기 위한 예시 문서",
        }
    ]
    assert document.json()["body"] == "# 수면"


def test_missing_wiki_returns_404(tmp_path: Path) -> None:
    response = client(tmp_path).get("/api/wiki/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Wiki document not found"}


def test_chat_requires_non_blank_prompt(tmp_path: Path) -> None:
    response = client(tmp_path).post("/api/chat", json={"prompt": " ", "baby_info": {}})

    assert response.status_code == 422


def test_chat_accepts_a_fresh_browser_profile_with_empty_birth_date(tmp_path: Path) -> None:
    response = client(tmp_path).post(
        "/api/chat",
        json={
            "prompt": "수면 질문",
            "baby_info": {"name": "", "birth_date": "", "notes": ""},
        },
    )

    assert response.status_code == 200
    assert "event: done" in response.text


def test_chat_rejects_oversized_profile_fields(tmp_path: Path) -> None:
    response = client(tmp_path).post(
        "/api/chat",
        json={
            "prompt": "수면 질문",
            "baby_info": {"name": "n" * 101, "notes": "n" * 2001},
        },
    )

    assert response.status_code == 422


def test_offline_chat_streams_tool_grounded_answer_and_done(tmp_path: Path) -> None:
    response = client(tmp_path).post(
        "/api/chat",
        json={
            "prompt": "아기가 잠을 안 자요",
            "baby_info": {"name": "아기", "birth_date": "2026-06-01", "notes": "건강함"},
        },
    )

    events = parse_sse(response.text)

    assert response.headers["content-type"].startswith("text/event-stream")
    assert events[-1] == ("done", {})
    answer = "".join(data["text"] for event, data in events if event == "delta")
    assert "신생아 수면 기초" in answer
    assert "개발 흐름을 확인하기 위한 예시 문서" in answer
    assert "not medical advice" in answer

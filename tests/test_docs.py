import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PAGES = {
    "01-end-to-end-architecture.md",
    "02-python-and-uv.md",
    "03-fastapi-and-sse.md",
    "04-pydantic-ai.md",
    "05-react-vite-and-bun.md",
    "06-knowledge-bundle.md",
    "07-docker-compose-and-nginx.md",
    "08-testing-and-debugging.md",
}
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`]+`")


def prose(document: Path) -> str:
    text = document.read_text(encoding="utf-8")
    return INLINE_CODE.sub("", CODE_BLOCK.sub("", text))


def test_reference_index_links_every_handbook_page() -> None:
    index = (ROOT / "docs/references/index.md").read_text(encoding="utf-8")

    assert {target for target in LINK.findall(index) if "://" not in target} == REFERENCE_PAGES


def test_all_local_documentation_links_resolve() -> None:
    failures: list[str] = []
    for document in (ROOT / "docs").rglob("*.md"):
        for target in LINK.findall(prose(document)):
            clean = target.split("#", 1)[0]
            if not clean or "://" in clean or clean.startswith("/"):
                continue
            if not (document.parent / clean).resolve().exists():
                failures.append(f"{document.relative_to(ROOT)} -> {target}")

    assert failures == []


def test_final_scaffold_spec_has_no_unresolved_placeholders() -> None:
    spec = (ROOT / "docs/specs/2026-07-28-project-scaffold.md").read_text(encoding="utf-8")

    assert not re.search(r"\b(TBD|TODO|FIXME)\b", spec)

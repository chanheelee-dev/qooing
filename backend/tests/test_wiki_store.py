from pathlib import Path

import pytest
from app.wiki_store import InvalidSlugError, WikiNotFoundError, WikiStore


def write_wiki(root: Path, slug: str = "sleep", title: str = "Sleep") -> None:
    path = root / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntype: Wiki\ntitle: {title}\ndescription: Basics\n"
        "sources: [/references/guide.md]\n---\n# Body\n",
        encoding="utf-8",
    )


def test_list_wiki_is_alphabetized_by_title(tmp_path: Path) -> None:
    write_wiki(tmp_path, "zulu", "Zulu")
    write_wiki(tmp_path, "alpha", "Alpha")

    summaries = WikiStore(tmp_path).list()

    assert [item.title for item in summaries] == ["Alpha", "Zulu"]


def test_read_returns_metadata_and_body(tmp_path: Path) -> None:
    write_wiki(tmp_path)

    document = WikiStore(tmp_path).read("sleep")

    assert document.slug == "sleep"
    assert document.type == "Wiki"
    assert document.sources == ["/references/guide.md"]
    assert document.body == "# Body"


@pytest.mark.parametrize("slug", ["../secret", "Bad Name", "nested/file", ""])
def test_read_rejects_unsafe_slugs(tmp_path: Path, slug: str) -> None:
    with pytest.raises(InvalidSlugError):
        WikiStore(tmp_path).read(slug)


def test_read_reports_missing_document(tmp_path: Path) -> None:
    with pytest.raises(WikiNotFoundError):
        WikiStore(tmp_path).read("missing")

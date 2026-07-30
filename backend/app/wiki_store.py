from __future__ import annotations

import builtins
import re
from pathlib import Path

import frontmatter

from .schemas import WikiDocument, WikiSummary

KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class InvalidSlugError(ValueError):
    pass


class WikiNotFoundError(FileNotFoundError):
    pass


class WikiStore:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def list(self) -> builtins.list[WikiSummary]:
        summaries = [
            self._summary(path) for path in self.root.glob("*.md") if path.name != "index.md"
        ]
        return sorted(summaries, key=lambda item: item.title.casefold())

    def read(self, slug: str) -> WikiDocument:
        if not KEBAB_CASE.fullmatch(slug):
            raise InvalidSlugError(slug)
        path = (self.root / f"{slug}.md").resolve()
        if path.parent != self.root:
            raise InvalidSlugError(slug)
        if not path.is_file():
            raise WikiNotFoundError(slug)
        post = frontmatter.load(path)
        raw_sources = post.get("sources", [])
        sources = raw_sources if isinstance(raw_sources, list) else []
        return WikiDocument(
            slug=slug,
            type=str(post.get("type", "Wiki")),
            title=str(post.get("title", slug)),
            description=str(post.get("description", "")),
            body=str(post.content).strip(),
            sources=[str(value) for value in sources],
        )

    def _summary(self, path: Path) -> WikiSummary:
        post = frontmatter.load(path)
        return WikiSummary(
            slug=path.stem,
            title=str(post.get("title", path.stem)),
            description=str(post.get("description", "")),
        )

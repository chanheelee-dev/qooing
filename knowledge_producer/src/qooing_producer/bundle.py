from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path, PurePosixPath

import frontmatter

REQUIRED_DIRECTORIES = ("references", "sources", "wiki")
EXPECTED_TYPES = {"references": "Reference", "sources": "Source", "wiki": "Wiki"}
KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
DATE_HEADING = re.compile(r"^## (\d{4}-\d{2}-\d{2})$", re.MULTILINE)


class BundleSecurityError(ValueError):
    pass


@dataclass(frozen=True)
class Violation:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _concept_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if path.name not in {"index.md", "log.md"} and path.is_file()
    )


def _resolve_bundle_path(root: Path, source: str, current: Path) -> Path | None:
    if "://" in source or source.startswith("#"):
        return None
    clean = source.split("#", 1)[0]
    if not clean:
        return None
    candidate = root / clean.lstrip("/") if clean.startswith("/") else current.parent / clean
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return Path("__outside_bundle__")
    return resolved


def validate_bundle(root: Path) -> list[Violation]:
    root = root.resolve()
    violations: list[Violation] = []

    directories = [root, *(path for path in root.rglob("*") if path.is_dir())]
    for path in root.rglob("*"):
        if path.is_symlink():
            violations.append(
                Violation(_relative(path, root), "symbolic links are not allowed in the bundle")
            )
    for directory in sorted(directories):
        index = directory / "index.md"
        if not index.is_file():
            violations.append(
                Violation(_relative(directory, root) or ".", "missing required index.md")
            )
            continue
        for link in MARKDOWN_LINK.findall(index.read_text(encoding="utf-8")):
            target = _resolve_bundle_path(root, link, index)
            if target is not None and not target.is_file():
                violations.append(
                    Violation(_relative(index, root), f"index link does not exist: {link}")
                )

    for name in REQUIRED_DIRECTORIES:
        directory = root / name
        if not directory.is_dir():
            violations.append(Violation(name, "missing required directory"))

    reference_log = root / "references/log.md"
    if not reference_log.is_file():
        violations.append(
            Violation("references/log.md", "missing required references/log.md audit log")
        )
    else:
        log_text = reference_log.read_text(encoding="utf-8")
        date_values = DATE_HEADING.findall(log_text)
        try:
            parsed_dates = [date.fromisoformat(value) for value in date_values]
        except ValueError:
            parsed_dates = []
        if not parsed_dates:
            violations.append(
                Violation("references/log.md", "audit log requires YYYY-MM-DD headings")
            )
        elif parsed_dates != sorted(parsed_dates, reverse=True):
            violations.append(
                Violation("references/log.md", "audit log dates must be newest first")
            )
        if not re.search(r"^\* .+", log_text, re.MULTILINE):
            violations.append(
                Violation("references/log.md", "audit log requires at least one decision entry")
            )

    for path in _concept_files(root):
        relative = _relative(path, root)
        if not KEBAB_CASE.fullmatch(path.stem):
            violations.append(Violation(relative, "concept filename must be lowercase kebab-case"))
        try:
            post = frontmatter.load(path)
        except Exception as exc:
            violations.append(Violation(relative, f"malformed YAML frontmatter: {exc}"))
            continue

        concept_type = post.get("type")
        if not concept_type:
            violations.append(Violation(relative, "missing required 'type' frontmatter"))
        top_directory = PurePosixPath(relative).parts[0]
        expected = EXPECTED_TYPES.get(top_directory)
        if expected and concept_type and concept_type != expected:
            violations.append(Violation(relative, f"type must be {expected}"))

        for field in ("title", "description", "timestamp"):
            if not post.get(field):
                violations.append(Violation(relative, f"missing recommended '{field}' frontmatter"))
        timestamp = post.get("timestamp")
        if timestamp and not isinstance(timestamp, (str, date, datetime)):
            violations.append(Violation(relative, "timestamp must be ISO 8601"))
        elif isinstance(timestamp, str):
            try:
                datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                violations.append(Violation(relative, "timestamp must be ISO 8601"))

        if concept_type == "Wiki":
            sources = post.get("sources", [])
            if not isinstance(sources, list):
                violations.append(Violation(relative, "sources must be a list"))
            else:
                for source in sources:
                    if not isinstance(source, str) or not source.startswith("/"):
                        violations.append(
                            Violation(relative, "wiki sources must use bundle-root absolute paths")
                        )
                        continue
                    target = _resolve_bundle_path(root, source, path)
                    if target is not None and not target.is_file():
                        violations.append(Violation(relative, f"source does not exist: {source}"))

        for link in MARKDOWN_LINK.findall(str(post.content)):
            target = _resolve_bundle_path(root, link, path)
            if target is not None and not target.is_file():
                violations.append(Violation(relative, f"local link does not exist: {link}"))

    return sorted(violations, key=lambda item: (item.path, item.message))


def _index_for(directory: Path, root: Path) -> str:
    title = "Knowledge Bundle" if directory == root else directory.name.replace("-", " ").title()
    entries: list[tuple[str, str]] = []
    for child in sorted(directory.iterdir()):
        if child.is_dir():
            entries.append(
                (child.name.casefold(), f"* [{child.name.title()}]({child.name}/index.md)")
            )
        elif child.suffix == ".md" and child.name not in {"index.md", "log.md"}:
            try:
                post = frontmatter.load(child)
            except Exception:
                continue
            label = str(post.get("title") or child.stem)
            description = str(post.get("description") or "")
            suffix = f" - {description}" if description else ""
            entries.append((label.casefold(), f"* [{label}]({child.name}){suffix}"))
    body = "\n".join(value for _, value in sorted(entries))
    return f"# {title}\n" + (f"\n{body}\n" if body else "\n")


def generate_indexes(root: Path) -> None:
    root = root.resolve()
    symlinks = [path for path in root.rglob("*") if path.is_symlink()]
    if symlinks:
        names = ", ".join(_relative(path, root) for path in symlinks)
        raise BundleSecurityError(f"symbolic links are not allowed in the bundle: {names}")
    directories = sorted(
        [root, *(path for path in root.rglob("*") if path.is_dir())],
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for directory in directories:
        (directory / "index.md").write_text(_index_for(directory, root), encoding="utf-8")

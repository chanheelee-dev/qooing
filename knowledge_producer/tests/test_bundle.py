from pathlib import Path

import pytest
from qooing_producer.bundle import (
    BundleSecurityError,
    generate_indexes,
    validate_bundle,
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def valid_bundle(root: Path) -> Path:
    write(root / "index.md", "# Bundle\n\n* [Wiki](wiki/index.md)\n")
    write(root / "references/index.md", "# References\n")
    write(
        root / "references/log.md",
        "# References Update Log\n\n## 2026-07-28\n"
        "* **Reliability**: Guide accepted as scaffold evidence.\n",
    )
    write(root / "sources/index.md", "# Sources\n")
    write(root / "wiki/index.md", "# Wiki\n\n* [Sleep](sleep.md) - Sleep basics\n")
    write(
        root / "wiki/sleep.md",
        "---\ntype: Wiki\ntitle: Sleep\ndescription: Sleep basics\n"
        "sources: [/references/guide.md]\ntimestamp: 2026-07-28T00:00:00Z\n---\nBody\n",
    )
    write(
        root / "references/guide.md",
        "---\ntype: Reference\ntitle: Guide\ndescription: Trusted guide\n"
        "timestamp: 2026-07-28T00:00:00Z\n---\nGuide\n",
    )
    return root


def test_valid_bundle_has_no_violations(tmp_path: Path) -> None:
    assert validate_bundle(valid_bundle(tmp_path)) == []


def test_validation_aggregates_structure_and_metadata_errors(tmp_path: Path) -> None:
    write(tmp_path / "wiki/Bad Name.md", "---\ntitle: Missing type\n---\nBody\n")

    messages = [violation.message for violation in validate_bundle(tmp_path)]

    assert any("missing required index.md" in message for message in messages)
    assert any("references/log.md" in message for message in messages)
    assert any("kebab-case" in message for message in messages)
    assert any("required 'type'" in message for message in messages)


def test_generate_indexes_is_stable_and_alphabetical(tmp_path: Path) -> None:
    root = valid_bundle(tmp_path)
    write(
        root / "wiki/alpha.md",
        "---\ntype: Wiki\ntitle: Alpha\ndescription: First\n"
        "timestamp: 2026-07-28T00:00:00Z\n---\nAlpha\n",
    )

    generate_indexes(root)
    first = (root / "wiki/index.md").read_text(encoding="utf-8")
    generate_indexes(root)
    second = (root / "wiki/index.md").read_text(encoding="utf-8")

    assert first == second
    assert first.index("[Alpha]") < first.index("[Sleep]")


def test_validation_reports_broken_wiki_source(tmp_path: Path) -> None:
    root = valid_bundle(tmp_path)
    (root / "references/guide.md").unlink()

    messages = [violation.message for violation in validate_bundle(root)]

    assert any("source does not exist" in message for message in messages)


def test_validation_reports_non_iso_timestamp(tmp_path: Path) -> None:
    root = valid_bundle(tmp_path)
    wiki = root / "wiki/sleep.md"
    wiki.write_text(
        wiki.read_text(encoding="utf-8").replace("2026-07-28T00:00:00Z", "not-a-timestamp"),
        encoding="utf-8",
    )

    messages = [violation.message for violation in validate_bundle(root)]

    assert any("timestamp must be ISO 8601" in message for message in messages)


def test_validation_reports_broken_index_link(tmp_path: Path) -> None:
    root = valid_bundle(tmp_path)
    (root / "wiki/index.md").write_text(
        "# Wiki\n\n* [Missing](missing.md) - Missing\n", encoding="utf-8"
    )

    messages = [violation.message for violation in validate_bundle(root)]

    assert any("index link does not exist" in message for message in messages)


def test_validation_reports_reference_log_dates_out_of_order(tmp_path: Path) -> None:
    root = valid_bundle(tmp_path)
    (root / "references/log.md").write_text(
        "# References Update Log\n\n## 2026-07-01\n* Older\n\n## 2026-07-28\n* Newer\n",
        encoding="utf-8",
    )

    messages = [violation.message for violation in validate_bundle(root)]

    assert any("newest first" in message for message in messages)


def test_generate_indexes_rejects_external_directory_symlinks(tmp_path: Path) -> None:
    root = valid_bundle(tmp_path / "bundle")
    external = tmp_path / "external"
    external.mkdir()
    (external / "index.md").write_text("do not overwrite", encoding="utf-8")
    (root / "linked").symlink_to(external, target_is_directory=True)

    with pytest.raises(BundleSecurityError):
        generate_indexes(root)

    assert (external / "index.md").read_text(encoding="utf-8") == "do not overwrite"

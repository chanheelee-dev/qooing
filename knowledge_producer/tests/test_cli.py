from pathlib import Path

import pytest
from qooing_producer.cli import main


def test_validate_returns_nonzero_and_prints_all_violations(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["validate", str(tmp_path)])
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "missing required index.md" in output
    assert "references/log.md" in output

from __future__ import annotations

from pathlib import Path

import pytest

from doc_sync.cli import main

FIXTURES_DIR = Path(__file__).parents[1] / "fixtures"


def _fixture_text(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def _fixture_json(name: str) -> str:
    return _fixture_text(name)


def _write_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _rendered_block_for_valid_manifest() -> str:
    return "\n".join(
        [
            "## API Reference",
            "",
            "Service: Billing API",
            "Version: v1",
            "",
            "| Method | Path | Description | Authentication |",
            "| --- | --- | --- | --- |",
            "| GET | /invoices | List invoices | OAuth2 |",
        ]
    )


def _docs_with_block(block: str) -> str:
    return "\n".join(
        [
            "# API Reference",
            "",
            "Intro text.",
            "<!-- DOCS_SYNC:START -->",
            block,
            "<!-- DOCS_SYNC:END -->",
            "",
            "Footer text.",
            "",
        ]
    )


def test_cli_write_updates_stale_docs(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = _write_file(tmp_path / "api" / "endpoints.json", _fixture_json("valid_endpoints.json"))
    output_path = _write_file(tmp_path / "docs" / "API_REFERENCE.md", _fixture_text("docs_with_markers_stale.md"))

    code = main(["--write", "--manifest", str(manifest_path), "--output", str(output_path)])

    out = capsys.readouterr()
    updated = output_path.read_text(encoding="utf-8")

    assert code == 0
    assert out.out.strip() == "Documentation updated."
    assert "Service: Billing API" in updated
    assert updated.startswith("# API Reference\n\nIntro text.\n")
    assert updated.endswith("\n\nFooter text.\n")


def test_cli_write_returns_zero_when_docs_current(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = _write_file(tmp_path / "api" / "endpoints.json", _fixture_json("valid_endpoints.json"))
    current_docs = _docs_with_block(_rendered_block_for_valid_manifest())
    output_path = _write_file(tmp_path / "docs" / "API_REFERENCE.md", current_docs)
    original = output_path.read_text(encoding="utf-8")

    code = main(["--write", "--manifest", str(manifest_path), "--output", str(output_path)])

    out = capsys.readouterr()

    assert code == 0
    assert out.out.strip() == "No update required."
    assert output_path.read_text(encoding="utf-8") == original


def test_cli_check_returns_zero_when_docs_current(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = _write_file(tmp_path / "manifest.json", _fixture_json("valid_endpoints.json"))
    output_path = _write_file(tmp_path / "output.md", _docs_with_block(_rendered_block_for_valid_manifest()))

    code = main(["--check", "--manifest", str(manifest_path), "--output", str(output_path)])

    out = capsys.readouterr()

    assert code == 0
    assert out.out.strip() == "Documentation is current."


def test_cli_check_returns_one_when_docs_stale(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = _write_file(tmp_path / "manifest.json", _fixture_json("valid_endpoints.json"))
    output_path = _write_file(tmp_path / "output.md", _fixture_text("docs_with_markers_stale.md"))
    original = output_path.read_text(encoding="utf-8")

    code = main(["--check", "--manifest", str(manifest_path), "--output", str(output_path)])

    out = capsys.readouterr()

    assert code == 1
    assert out.out.strip() == "Documentation is stale."
    assert output_path.read_text(encoding="utf-8") == original


def test_cli_supports_custom_manifest_and_output_paths(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest_path = _write_file(tmp_path / "custom" / "manifest.json", _fixture_json("valid_endpoints.json"))
    output_path = _write_file(tmp_path / "custom" / "docs.md", _fixture_text("docs_with_markers_stale.md"))

    code = main(["--write", "--manifest", str(manifest_path), "--output", str(output_path)])

    out = capsys.readouterr()

    assert code == 0
    assert out.out.strip() == "Documentation updated."


def test_cli_uses_default_manifest_and_output_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_file(tmp_path / "api" / "endpoints.json", _fixture_json("valid_endpoints.json"))
    _write_file(tmp_path / "docs" / "API_REFERENCE.md", _docs_with_block(_rendered_block_for_valid_manifest()))
    monkeypatch.chdir(tmp_path)

    code = main(["--check"])

    out = capsys.readouterr()

    assert code == 0
    assert out.out.strip() == "Documentation is current."


def test_cli_missing_manifest_returns_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    output_path = _write_file(tmp_path / "output.md", _fixture_text("docs_with_markers_stale.md"))

    code = main(["--check", "--manifest", str(tmp_path / "missing.json"), "--output", str(output_path)])

    out = capsys.readouterr()

    assert code == 2
    assert "Error: Manifest file not found:" in out.err


def test_cli_missing_output_returns_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = _write_file(tmp_path / "manifest.json", _fixture_json("valid_endpoints.json"))

    code = main(["--check", "--manifest", str(manifest_path), "--output", str(tmp_path / "missing.md")])

    out = capsys.readouterr()

    assert code == 2
    assert "Error: Output documentation file not found:" in out.err


def test_cli_invalid_json_returns_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = _write_file(tmp_path / "manifest.json", _fixture_json("invalid_json.json"))
    output_path = _write_file(tmp_path / "output.md", _fixture_text("docs_with_markers_stale.md"))

    code = main(["--check", "--manifest", str(manifest_path), "--output", str(output_path)])

    out = capsys.readouterr()

    assert code == 2
    assert "Error: Invalid JSON in manifest" in out.err


def test_cli_invalid_manifest_data_returns_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = _write_file(tmp_path / "manifest.json", _fixture_json("empty_endpoints.json"))
    output_path = _write_file(tmp_path / "output.md", _fixture_text("docs_with_markers_stale.md"))

    code = main(["--check", "--manifest", str(manifest_path), "--output", str(output_path)])

    out = capsys.readouterr()

    assert code == 2
    assert "Error: Manifest 'endpoints' must be a non-empty list" in out.err


def test_cli_unsupported_http_method_returns_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest_path = _write_file(
        tmp_path / "manifest.json",
        "\n".join(
            [
                "{",
                '  "serviceName": "Billing API",',
                '  "version": "v1",',
                '  "endpoints": [',
                "    {",
                '      "method": "get",',
                '      "path": "/invoices",',
                '      "summary": "List invoices",',
                '      "authentication": "OAuth2"',
                "    }",
                "  ]",
                "}",
            ]
        ),
    )
    output_path = _write_file(tmp_path / "output.md", _fixture_text("docs_with_markers_stale.md"))

    code = main(["--check", "--manifest", str(manifest_path), "--output", str(output_path)])

    out = capsys.readouterr()

    assert code == 2
    assert "has unsupported HTTP method" in out.err


@pytest.mark.parametrize(
    "fixture_name",
    [
        "docs_missing_start_marker.md",
        "docs_missing_end_marker.md",
        "docs_invalid_marker_order.md",
        "docs_duplicate_markers.md",
    ],
)
def test_cli_invalid_marker_configuration_returns_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fixture_name: str
) -> None:
    manifest_path = _write_file(tmp_path / "manifest.json", _fixture_json("valid_endpoints.json"))
    output_path = _write_file(tmp_path / "output.md", _fixture_text(fixture_name))
    original = output_path.read_text(encoding="utf-8")

    code = main(["--check", "--manifest", str(manifest_path), "--output", str(output_path)])

    out = capsys.readouterr()

    assert code == 2
    assert "Error:" in out.err
    assert output_path.read_text(encoding="utf-8") == original


def test_cli_rejects_both_modes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = _write_file(tmp_path / "manifest.json", _fixture_json("valid_endpoints.json"))
    output_path = _write_file(tmp_path / "output.md", _fixture_text("docs_with_markers_stale.md"))

    code = main(
        ["--write", "--check", "--manifest", str(manifest_path), "--output", str(output_path)]
    )

    out = capsys.readouterr()

    assert code == 2
    assert "Error: Invalid command arguments:" in out.err


def test_cli_rejects_missing_mode_argument(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    manifest_path = _write_file(tmp_path / "manifest.json", _fixture_json("valid_endpoints.json"))
    output_path = _write_file(tmp_path / "output.md", _fixture_text("docs_with_markers_stale.md"))

    code = main(["--manifest", str(manifest_path), "--output", str(output_path)])

    out = capsys.readouterr()

    assert code == 2
    assert "Error: Invalid command arguments:" in out.err


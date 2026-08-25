from __future__ import annotations

from doc_sync.models import Manifest


def normalize_markdown_cell(value: str) -> str:
    """Normalize a cell value to keep markdown tables valid."""
    normalized = value.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    normalized = normalized.replace("|", "\\|")
    return normalized.strip()


def render_api_reference_section(manifest: Manifest) -> str:
    """Render deterministic API reference markdown from a validated manifest."""
    lines = [
        "## API Reference",
        "",
        f"Service: {normalize_markdown_cell(manifest.service_name)}",
        f"Version: {normalize_markdown_cell(manifest.version)}",
        "",
        "| Method | Path | Description | Authentication |",
        "| --- | --- | --- | --- |",
    ]

    for endpoint in manifest.endpoints:
        method = normalize_markdown_cell(endpoint.method)
        path = normalize_markdown_cell(endpoint.path)
        description = normalize_markdown_cell(endpoint.summary)
        authentication = normalize_markdown_cell(endpoint.authentication)
        lines.append(f"| {method} | {path} | {description} | {authentication} |")

    return "\n".join(lines)

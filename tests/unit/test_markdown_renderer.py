from doc_sync.markdown_renderer import normalize_markdown_cell, render_api_reference_section
from doc_sync.models import Endpoint, Manifest


def test_normalize_markdown_cell_replaces_pipes_and_line_breaks() -> None:
    value = "OAuth|Key\r\nRequired\nNow\rPlease"

    normalized = normalize_markdown_cell(value)

    assert normalized == "OAuth\\|Key Required Now Please"


def test_render_api_reference_section_contains_required_fields_and_headers() -> None:
    manifest = Manifest(
        service_name="Billing API",
        version="v1",
        endpoints=[
            Endpoint(
                method="GET",
                path="/invoices",
                summary="List invoices",
                authentication="OAuth2",
            )
        ],
    )

    content = render_api_reference_section(manifest)

    assert "Service: Billing API" in content
    assert "Version: v1" in content
    assert "| Method | Path | Description | Authentication |" in content
    assert "| GET | /invoices | List invoices | OAuth2 |" in content


def test_render_api_reference_section_normalizes_endpoint_values() -> None:
    manifest = Manifest(
        service_name="Billing|API",
        version="v1\nalpha",
        endpoints=[
            Endpoint(
                method="POST",
                path="/invoices|draft",
                summary="Create\r\nInvoice",
                authentication="Api\nKey",
            )
        ],
    )

    content = render_api_reference_section(manifest)

    assert "Service: Billing\\|API" in content
    assert "Version: v1 alpha" in content
    assert "| POST | /invoices\\|draft | Create Invoice | Api Key |" in content


def test_render_api_reference_section_is_deterministic() -> None:
    manifest = Manifest(
        service_name="Payments API",
        version="v2",
        endpoints=[
            Endpoint(
                method="PUT",
                path="/payments/{id}",
                summary="Update payment",
                authentication="OAuth2",
            )
        ],
    )

    first = render_api_reference_section(manifest)
    second = render_api_reference_section(manifest)

    assert first == second

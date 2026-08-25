from doc_sync.models import Endpoint, Manifest


def test_endpoint_and_manifest_dataclasses_store_values() -> None:
    endpoint = Endpoint(
        method="GET",
        path="/users",
        summary="List users",
        authentication="OAuth2",
    )

    manifest = Manifest(service_name="Users API", version="v1", endpoints=[endpoint])

    assert manifest.service_name == "Users API"
    assert manifest.version == "v1"
    assert manifest.endpoints == [endpoint]

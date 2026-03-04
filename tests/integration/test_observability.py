import pytest


@pytest.mark.asyncio
async def test_observability_health_endpoint(client):
    response = await client.get("/observability/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "ready"


@pytest.mark.asyncio
async def test_request_metadata_endpoint_returns_request_stats(client):
    await client.get("/health")
    response = await client.get("/observability/request-metadata")

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    data = payload["data"]

    assert "total_requests" in data
    assert "path_total" in data
    assert "status_total" in data
    assert "failure_total" in data
    assert "total_requests" in data
    assert "path_total" in data
    assert "status_total" in data
    assert "failure_total" in data
    assert data["total_requests"] >= 1


@pytest.mark.asyncio
async def test_request_metadata_excludes_internal_paths(client):
    baseline_response = await client.get("/observability/request-metadata")
    baseline = baseline_response.json()["data"]
    await client.get("/health")
    await client.get("/observability/health")
    await client.get("/metrics")
    after_internal = await client.get("/observability/request-metadata")

    after_data = after_internal.json()["data"]

    assert after_data["total_requests"] == baseline["total_requests"] + 1
    assert "/metrics" not in after_data["path_total"]
    assert "/observability/request-metadata" not in after_data["path_total"]

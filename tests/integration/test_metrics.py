import pytest


@pytest.mark.asyncio
async def test_metrics_endpoint_returns_prometheus_text(client):
    response = await client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    body = response.text
    assert "http_requests_total" in body
    assert "http_request_latency_seconds" in body
    assert "http_requests_in_progress" in body

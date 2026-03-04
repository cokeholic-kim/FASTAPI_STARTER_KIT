import asyncio

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient):
    response = await client.post(
        "/users",
        json={"email": "test@example.com", "name": "Test User"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    response = await client.get("/users/99999")

    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_create_user_duplicate_email_is_rejected(client: AsyncClient):
    first = await client.post(
        "/users",
        json={"email": "dup@example.com", "name": "first"},
    )
    assert first.status_code == 201

    second = await client.post(
        "/users",
        json={"email": "dup@example.com", "name": "second"},
    )
    assert second.status_code == 409
    assert second.json()["error_code"] == "DUPLICATE"


@pytest.mark.asyncio
async def test_concurrent_duplicate_user_creation_is_handled_as_409(client: AsyncClient):
    payload = {"email": "race@example.com", "name": "Race User"}

    async def create() -> int:
        response = await client.post("/users", json=payload)
        return response.status_code

    first_status, second_status = await asyncio.gather(create(), create())
    assert sorted([first_status, second_status]) == [201, 409]

    list_response = await client.get("/users")
    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_delete_user_returns_no_content(client: AsyncClient):
    create_response = await client.post(
        "/users",
        json={"email": "delete@example.com", "name": "Delete User"},
    )
    assert create_response.status_code == 201

    user_id = create_response.json()["data"]["id"]

    delete_response = await client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = await client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

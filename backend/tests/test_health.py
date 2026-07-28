import pytest

@pytest.mark.asyncio
async def test_public_drops(client):
    response = await client.get("/api/drops")
    print("Success")
    assert response.status_code == 200
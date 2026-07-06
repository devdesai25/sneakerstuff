async def test_public_drops(client):
    response = await client.get("/api/drops")
    assert response.status_code == 200
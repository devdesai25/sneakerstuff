import pytest
from httpx import AsyncClient
from backend.models.products import Product

@pytest.mark.asyncio
async def test_get_cart_empty(client: AsyncClient, user_headers: dict):
    """Test getting cart when it's empty."""
    response = await client.get("/api/cart", headers=user_headers)
    
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_add_to_cart_success(client: AsyncClient, user_headers: dict, product: Product):
    """Test adding an item to the cart."""
    response = await client.post(
        "/api/cart",
        json={"product_id": product.product_id, "quantity": 2},
        headers=user_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product.product_id
    assert data["quantity"] == 2

@pytest.mark.asyncio
async def test_add_to_cart_unauthorized(client: AsyncClient, product: Product):
    """Test adding to cart without auth."""
    response = await client.post(
        "/api/cart",
        json={"product_id": product.product_id, "quantity": 2}
    )
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_cart_with_items(client: AsyncClient, user_headers: dict, product: Product):
    """Test getting cart with items."""
    await client.post(
        "/api/cart",
        json={"product_id": product.product_id, "quantity": 2},
        headers=user_headers
    )
    
    response = await client.get("/api/cart", headers=user_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["product_id"] == product.product_id
    assert data[0]["quantity"] == 2
    assert data[0]["name"] == product.name

@pytest.mark.asyncio
async def test_delete_cart_item(client: AsyncClient, user_headers: dict, product: Product):
    """Test deleting an item from the cart."""
    await client.post(
        "/api/cart",
        json={"product_id": product.product_id, "quantity": 2},
        headers=user_headers
    )
    
    response = await client.delete(
        f"/api/cart/{product.product_id}",
        headers=user_headers
    )
    
    assert response.status_code == 200
    assert response.json() == {"Message": "Product Deleted From Cart Successfully"}
    
    # Verify it's empty
    get_res = await client.get("/api/cart", headers=user_headers)
    assert get_res.json() == []

@pytest.mark.asyncio
async def test_patch_cart_item(client: AsyncClient, user_headers: dict, product: Product):
    """Test updating the quantity of a cart item."""
    await client.post(
        "/api/cart",
        json={"product_id": product.product_id, "quantity": 2},
        headers=user_headers
    )
    
    response = await client.patch(
        f"/api/cart/{product.product_id}",
        json={"quantity": 5},
        headers=user_headers
    )
    
    assert response.status_code == 200
    assert response.json()["quantity"] == 5

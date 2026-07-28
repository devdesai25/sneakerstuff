import pytest
from httpx import AsyncClient
from backend.models.products import Product

@pytest.mark.asyncio
async def test_get_products(client: AsyncClient, product: Product):
    """Test fetching list of products (public)."""
    response = await client.get("/api/products")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == product.name

@pytest.mark.asyncio
async def test_create_product_admin(client: AsyncClient, admin_headers: dict):
    """Test creating a product as admin."""
    new_product = {
        "name": "Admin Created Product",
        "description": "Admin description",
        "price": 100.0,
        "stock": 50,
        "images": "http://example.com/img.png"
    }
    
    response = await client.post(
        "/api/admin/create",
        json=new_product,
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Admin Created Product"
    assert data["price"] == 100.0

@pytest.mark.asyncio
async def test_create_product_forbidden(client: AsyncClient, user_headers: dict):
    """Test creating a product as normal user."""
    new_product = {
        "name": "User Created Product",
        "description": "User description",
        "price": 100.0,
        "stock": 50,
        "images": "http://example.com/img.png"
    }
    
    response = await client.post(
        "/api/admin/create",
        json=new_product,
        headers=user_headers
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"

@pytest.mark.asyncio
async def test_update_product_admin(client: AsyncClient, admin_headers: dict, product: Product):
    """Test updating a product as admin."""
    update_data = {
        "price": 150.0,
        "stock": 75
    }
    
    response = await client.patch(
        f"/api/admin/update/{product.product_id}",
        json=update_data,
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 150.0
    assert data["stock"] == 75

@pytest.mark.asyncio
async def test_delete_product_admin(client: AsyncClient, admin_headers: dict, product: Product):
    """Test deleting a product as admin."""
    response = await client.delete(
        f"/api/admin/delete/{product.product_id}",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    assert response.json() == {"message": "Product deleted successfully"}

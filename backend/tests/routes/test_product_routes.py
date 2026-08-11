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

@pytest.mark.asyncio
async def test_toggle_product_visibility_admin(client: AsyncClient, admin_headers: dict, product: Product):
    """Test toggling product visibility as admin."""
    # Initially visible
    assert product.is_visible is True
    
    # Toggle to hidden
    res1 = await client.patch(f"/api/admin/products/{product.product_id}/toggle-visibility", headers=admin_headers)
    assert res1.status_code == 200
    assert res1.json()["is_visible"] is False

    # Hidden product should not be in public GET /api/products by default
    res2 = await client.get("/api/products")
    assert res2.status_code == 200
    ids = [p["product_id"] for p in res2.json()]
    assert product.product_id not in ids

    # Hidden product IS returned when include_hidden=true
    res3 = await client.get("/api/products?include_hidden=true")
    assert res3.status_code == 200
    ids3 = [p["product_id"] for p in res3.json()]
    assert product.product_id in ids3

@pytest.mark.asyncio
async def test_toggle_product_reserved_admin(client: AsyncClient, admin_headers: dict, user_headers: dict, product: Product):
    """Test toggling product drop-reserved status as admin and verifying cart block."""
    # Initially not reserved
    assert product.is_reserved_for_drop is False

    # Toggle to reserved
    res1 = await client.patch(f"/api/admin/products/{product.product_id}/toggle-reserved", headers=admin_headers)
    assert res1.status_code == 200
    assert res1.json()["is_reserved_for_drop"] is True

    # Try adding reserved product to cart -> should fail 400
    cart_payload = {
        "product_id": product.product_id,
        "quantity": 1,
        "size": "US 9"
    }
    res2 = await client.post("/api/cart", json=cart_payload, headers=user_headers)
    assert res2.status_code == 400
    assert "reserved for an upcoming drop" in res2.json()["detail"]


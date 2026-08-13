from unittest.mock import MagicMock, patch

from fastapi import HTTPException
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.products import Product
from backend.models.users import User
from backend.schemas.product import ProductCreate, ProductUpdate
from backend.services.product_service import product_add, product_delete, product_update


@pytest.mark.asyncio
async def test_product_add_success(db: AsyncSession, admin_user: User):
    """Test successful product creation."""
    new_product = ProductCreate(
        name="Test Product 1",
        description="A cool product",
        price=100.0,
        stock=50,
        images="http://example.com/img.png"
    )
    
    result = await product_add(new_product=new_product, admin=admin_user, db=db)
    
    assert result.name == "Test Product 1"
    assert result.created_by == admin_user.id
    
    # Verify in DB
    db_product = (
        await db.execute(select(Product).where(Product.name == "Test Product 1"))
    ).scalar_one_or_none()
    assert db_product is not None
    assert db_product.stock == 50

@pytest.mark.asyncio
async def test_product_add_duplicate(db: AsyncSession, admin_user: User, product: Product):
    """Test adding duplicate product name."""
    duplicate_product = ProductCreate(
        name=product.name,
        description="Duplicate",
        price=50.0,
        stock=10,
        images="http://example.com/img2.png"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await product_add(new_product=duplicate_product, admin=admin_user, db=db)
        
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Duplicate Value Inserted"

@pytest.mark.asyncio
async def test_product_add_integrity_error(db: AsyncSession, admin_user: User):
    """Test product creation when DB integrity error occurs."""
    new_product = ProductCreate(
        name="Test Product Integrity",
        description="A cool product",
        price=100.0,
        stock=50,
        images="http://example.com/img.png"
    )
    
    with patch("sqlalchemy.ext.asyncio.AsyncSession.commit") as mock_commit:
        mock_commit.side_effect = IntegrityError(None, None, Exception())
        
        with pytest.raises(HTTPException) as exc_info:
            await product_add(new_product=new_product, admin=admin_user, db=db)
            
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Database Integrity Error"

@pytest.mark.asyncio
async def test_product_delete_success(db: AsyncSession, product: Product):
    """Test successful product deletion."""
    product_id = product.product_id
    
    result = await product_delete(product_id=product_id, db=db)
    assert result["message"] == "Product deleted successfully"
    
    # Verify deletion
    db_product = (
        await db.execute(select(Product).where(Product.product_id == product_id))
    ).scalar_one_or_none()
    assert db_product is None

@pytest.mark.asyncio
async def test_product_delete_not_found(db: AsyncSession):
    """Test deleting non-existent product."""
    with pytest.raises(HTTPException) as exc_info:
        await product_delete(product_id=9999, db=db)
        
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Product not found"

@pytest.mark.asyncio
async def test_product_delete_used_in_drop(db: AsyncSession, product: Product, drop):
    """Test deleting product that is associated with a drop."""
    with pytest.raises(HTTPException) as exc_info:
        await product_delete(product_id=product.product_id, db=db)
        
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Cannot delete a product that is used in a drop"

@pytest.mark.asyncio
async def test_product_delete_integrity_error(db: AsyncSession, product: Product):
    """Test product deletion when DB integrity error occurs."""
    with patch("sqlalchemy.ext.asyncio.AsyncSession.commit") as mock_commit:
        mock_commit.side_effect = IntegrityError(None, None, Exception())
        
        with pytest.raises(HTTPException) as exc_info:
            await product_delete(product_id=product.product_id, db=db)
            
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Database Integrity Error"

@pytest.mark.asyncio
async def test_product_update_success(db: AsyncSession, product: Product):
    """Test successful product update."""
    update_data = ProductUpdate(
        price=199.99,
        stock=150
    )
    
    result = await product_update(product_id=product.product_id, update_product=update_data, db=db)
    
    assert result.price == 199.99
    assert result.stock == 150
    assert result.name == product.name # Unchanged

@pytest.mark.asyncio
async def test_product_update_not_found(db: AsyncSession):
    """Test updating non-existent product."""
    update_data = ProductUpdate(price=199.99)
    with pytest.raises(HTTPException) as exc_info:
        await product_update(product_id=9999, update_product=update_data, db=db)
        
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_product_update_integrity_error(db: AsyncSession, product: Product):
    """Test product update when DB integrity error occurs."""
    update_data = ProductUpdate(price=199.99)
    with patch("sqlalchemy.ext.asyncio.AsyncSession.commit") as mock_commit:
        mock_commit.side_effect = IntegrityError(None, None, Exception())
        
        with pytest.raises(HTTPException) as exc_info:
            await product_update(product_id=product.product_id, update_product=update_data, db=db)
            
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Database Integrity Error"

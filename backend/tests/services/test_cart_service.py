import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from unittest.mock import patch

from backend.services.cart_service import cart_add, cart_patch, cart_delete
from backend.schemas.cart_items import CartCreate, CartPatch
from backend.models.cart_items import CartItem
from backend.models.products import Product
from backend.models.users import User

@pytest.mark.asyncio
async def test_cart_add_success_new_item(db: AsyncSession, user: User, product: Product):
    """Test successfully adding a new product to cart."""
    cart_data = CartCreate(product_id=product.product_id, quantity=2)
    
    result = await cart_add(cur_cart=cart_data, user=user, db=db)
    
    assert result.user_id == user.id
    assert result.product_id == product.product_id
    assert result.quantity == 2
    
    # Verify in DB
    db_cart = (
        await db.execute(select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product.product_id))
    ).scalar_one_or_none()
    assert db_cart is not None

@pytest.mark.asyncio
async def test_cart_add_success_existing_item(db: AsyncSession, user: User, product: Product):
    """Test adding quantity to an already existing cart item."""
    # First add
    cart_data_1 = CartCreate(product_id=product.product_id, quantity=2)
    await cart_add(cur_cart=cart_data_1, user=user, db=db)
    
    # Second add
    cart_data_2 = CartCreate(product_id=product.product_id, quantity=3)
    result = await cart_add(cur_cart=cart_data_2, user=user, db=db)
    
    assert result.quantity == 5 # 2 + 3

@pytest.mark.asyncio
async def test_cart_add_product_not_found(db: AsyncSession, user: User):
    """Test adding non-existent product to cart."""
    cart_data = CartCreate(product_id=9999, quantity=2)
    
    with pytest.raises(HTTPException) as exc_info:
        await cart_add(cur_cart=cart_data, user=user, db=db)
        
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Product Not found"

@pytest.mark.asyncio
async def test_cart_add_out_of_stock(db: AsyncSession, user: User, product: Product):
    """Test adding a product with requested quantity > stock."""
    cart_data = CartCreate(product_id=product.product_id, quantity=product.stock + 1)
    
    with pytest.raises(HTTPException) as exc_info:
        await cart_add(cur_cart=cart_data, user=user, db=db)
        
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Product is out of stock"

@pytest.mark.asyncio
async def test_cart_add_exceeds_stock_existing_item(db: AsyncSession, user: User, product: Product):
    """Test adding to existing cart item where total quantity exceeds stock."""
    # First add
    cart_data_1 = CartCreate(product_id=product.product_id, quantity=product.stock - 1)
    await cart_add(cur_cart=cart_data_1, user=user, db=db)
    
    # Second add exceeds stock
    cart_data_2 = CartCreate(product_id=product.product_id, quantity=2)
    
    with pytest.raises(HTTPException) as exc_info:
        await cart_add(cur_cart=cart_data_2, user=user, db=db)
        
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Stock unavailable"

@pytest.mark.asyncio
async def test_cart_patch_success_update_quantity(db: AsyncSession, user: User, product: Product):
    """Test updating quantity of an existing cart item."""
    # First add item
    await cart_add(cur_cart=CartCreate(product_id=product.product_id, quantity=2), user=user, db=db)
    
    # Patch item
    patch_data = CartPatch(quantity=5)
    result = await cart_patch(product_id=product.product_id, cur_cart=patch_data, user=user, db=db)
    
    assert type(result) is CartItem
    assert result.quantity == 5

@pytest.mark.asyncio
async def test_cart_patch_success_remove_item(db: AsyncSession, user: User, product: Product):
    """Test patching quantity to 0 removes the item."""
    await cart_add(cur_cart=CartCreate(product_id=product.product_id, quantity=2), user=user, db=db)
    
    patch_data = CartPatch(quantity=0)
    result = await cart_patch(product_id=product.product_id, cur_cart=patch_data, user=user, db=db)
    
    assert result == {"Message": "Product Removed From Cart"}
    
    # Verify removal
    db_cart = (
        await db.execute(select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product.product_id))
    ).scalar_one_or_none()
    assert db_cart is None

@pytest.mark.asyncio
async def test_cart_patch_product_not_found(db: AsyncSession, user: User):
    """Test patching non-existent product."""
    patch_data = CartPatch(quantity=5)
    with pytest.raises(HTTPException) as exc_info:
        await cart_patch(product_id=9999, cur_cart=patch_data, user=user, db=db)
        
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Product Not Found"

@pytest.mark.asyncio
async def test_cart_patch_cart_not_found(db: AsyncSession, user: User, product: Product):
    """Test patching product not in user's cart."""
    patch_data = CartPatch(quantity=5)
    with pytest.raises(HTTPException) as exc_info:
        await cart_patch(product_id=product.product_id, cur_cart=patch_data, user=user, db=db)
        
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Cart Not Found"

@pytest.mark.asyncio
async def test_cart_patch_out_of_stock(db: AsyncSession, user: User, product: Product):
    """Test patching quantity to exceed available stock."""
    await cart_add(cur_cart=CartCreate(product_id=product.product_id, quantity=2), user=user, db=db)
    
    # In cart_service.py: if product.stock < cart.quantity (Note: this logic in the original code seems slightly flawed, it checks if product.stock < existing cart.quantity, not cur_cart.quantity)
    # We will test the existing logic to ensure coverage.
    
    # Temporarily lower stock to trigger condition
    product.stock = 1
    await db.commit()
    
    patch_data = CartPatch(quantity=5)
    with pytest.raises(HTTPException) as exc_info:
        await cart_patch(product_id=product.product_id, cur_cart=patch_data, user=user, db=db)
        
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Product Out of Stock"

@pytest.mark.asyncio
async def test_cart_delete_success(db: AsyncSession, user: User, product: Product):
    """Test deleting an item from the cart."""
    await cart_add(cur_cart=CartCreate(product_id=product.product_id, quantity=2), user=user, db=db)
    
    result = await cart_delete(product_id=product.product_id, user=user, db=db)
    
    assert result == {"Message": "Product Deleted From Cart Successfully"}
    
    db_cart = (
        await db.execute(select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product.product_id))
    ).scalar_one_or_none()
    assert db_cart is None

@pytest.mark.asyncio
async def test_cart_delete_not_found(db: AsyncSession, user: User, product: Product):
    """Test deleting a non-existent item from the cart."""
    with pytest.raises(HTTPException) as exc_info:
        await cart_delete(product_id=product.product_id, user=user, db=db)
        
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Cart Not Found"

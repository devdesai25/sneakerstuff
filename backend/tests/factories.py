from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import select

from backend.auth.jwt import hash_password
from backend.enums.drop_status import DropStatus
from backend.models.drops import Drop
from backend.models.product_sizes import ProductSize
from backend.models.products import Product
from backend.models.users import User


async def create_user(db, **kwargs):
    defaults = {
        "username": "testuser",
        "email": "test@test.com",
        "hashed_password": hash_password("password123"),
        "role": "user"
    }
    defaults.update(kwargs)
    user = User(**defaults)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_product(db, **kwargs) -> Product:
    """
    Creates a valid Product and seeds default ProductSize entries.
    Any field can be overridden using kwargs.
    """
    defaults = {
        "name": "Nike Dunk Low Panda",
        "description": "Test Product",
        "price": 10,
        "stock": 200,
        "images": "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcRmTrFwafYTR3xV0nCO3Pnr5o5eegfzAMgrxIO1hvQ2KLY3zchBJtbaXSzJKu-t-AjsghmBZJkXIo0WYTUOza58BnVnjx0pgzw8BHRYCOf-EclM_ICbbVGctg",
    }
    defaults.update(kwargs)

    if "created_by" not in defaults or defaults["created_by"] is None:
        res = await db.execute(select(User.id).limit(1))
        user_id = res.scalar_one_or_none()
        if not user_id:
            u = await create_user(db, username="factory_admin", role="admin")
            user_id = u.id
        defaults["created_by"] = user_id

    product = Product(**defaults)
    db.add(product)
    await db.commit()
    await db.refresh(product)

    # Seed ProductSize records so cart and order operations succeed in tests
    sizes = ["US 7", "US 8", "US 9", "US 10", "US 11"]
    for sz in sizes:
        db.add(ProductSize(product_id=product.product_id, size=sz, stock=50))
    await db.commit()

    return product


async def create_drop(
    db, 
    product, 
    **kwargs,
):
    defaults = {
        "product_id": product.product_id,
        "product_name": product.name,
        "product_price": product.price,
        "product_image": product.images,
        "drop_inventory": 5,
        "status": DropStatus.DRAFT,
        "is_visible": True,
        "opens_at": datetime.now(timezone.utc) + timedelta(hours=1),
        "closes_at": datetime.now(timezone.utc) + timedelta(hours=2),
    }
    defaults.update(kwargs)
    drop = Drop(**defaults)
    db.add(drop)
    await db.commit()
    await db.refresh(drop)
    return drop
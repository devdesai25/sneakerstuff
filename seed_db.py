import sys
sys.path.insert(0, ".")
import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from backend.database import AsyncSessionLocal, Base, engine
import backend.models
from backend.models.users import User
from backend.models.products import Product
from backend.models.product_sizes import ProductSize
from backend.models.drops import Drop
from backend.auth.jwt import hash_password

async def seed():
    print("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 1. Seed Admin User
        user = (await db.execute(select(User).where(User.username == "admin"))).scalar_one_or_none()
        if not user:
            user = User(
                username="admin",
                email="admin@sneakerstuff.com",
                hashed_password=hash_password("admin123"),
                role="admin"
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"Created admin user (ID {user.id})")
        else:
            print(f"Admin user already exists (ID {user.id})")

        # 2. Seed Sample Products
        product = (await db.execute(select(Product))).scalars().first()
        if not product:
            product = Product(
                name="Nike Air Jordan 1 High OG 'Chicago'",
                description="The legendary Air Jordan 1 in the iconic Chicago colorway.",
                price=180.00,
                stock=50,
                created_by=user.id,
                images="https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600"
            )
            db.add(product)
            await db.commit()
            await db.refresh(product)
            print(f"Created sample product (ID {product.product_id})")

            for sz in ["US 7", "US 7.5", "US 8", "US 8.5", "US 9", "US 9.5", "US 10", "US 10.5", "US 11", "US 11.5", "US 12"]:
                ps = ProductSize(product_id=product.product_id, size=sz, stock=10)
                db.add(ps)
            await db.commit()
        else:
            print(f"Product already exists (ID {product.product_id})")

        # 2b. Seed Drop-Reserved Product
        reserved_prod = (await db.execute(select(Product).where(Product.name.ilike("%Travis Scott%")))).scalars().first()
        if not reserved_prod:
            reserved_prod = Product(
                name="Travis Scott x Air Jordan 1 Low 'Reverse Mocha'",
                description="Upcoming grail reserved exclusively for the shock drop raffle. Preview only.",
                price=190.00,
                stock=25,
                created_by=user.id,
                images="https://images.unsplash.com/photo-1552346154-21d32810aba3?q=80&w=600",
                is_reserved_for_drop=True,
                is_visible=True
            )
            db.add(reserved_prod)
            await db.commit()
            await db.refresh(reserved_prod)
            for sz in ["US 7", "US 8", "US 9", "US 10", "US 11"]:
                db.add(ProductSize(product_id=reserved_prod.product_id, size=sz, stock=5))
            await db.commit()
            print(f"Created sample drop-reserved product (ID {reserved_prod.product_id})")

        # 3. Seed Sample Drop
        drop = (await db.execute(select(Drop))).scalars().first()
        if not drop:
            now = datetime.now(timezone.utc)
            drop = Drop(
                product_id=product.product_id,
                product_name=product.name,
                product_price=product.price,
                product_image=product.images,
                drop_inventory=15,
                opens_at=now - timedelta(hours=1), # Currently open
                closes_at=now + timedelta(hours=23),
                status="ENTRY_OPEN",
                is_visible=True
            )
            db.add(drop)
            await db.commit()
            await db.refresh(drop)
            print(f"Created live drop (ID {drop.drop_id})")
        else:
            print(f"Drop already exists (ID {drop.drop_id})")

    print("\nDatabase successfully initialized and seeded!")

if __name__ == "__main__":
    asyncio.run(seed())

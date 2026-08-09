import sys
sys.path.insert(0, ".")
import asyncio
from backend.database import AsyncSessionLocal
from backend.models.products import Product
from backend.models.product_sizes import ProductSize
from sqlalchemy import select

async def seed_products():
    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(Product))).scalars().all()
        if existing:
            print(f"Products already exist in DB ({len(existing)} products found).")
            return existing[0].product_id

        # Seed sample product
        p = Product(
            name="Nike Air Force 1 '07",
            description="Iconic leather sneaker with Nike Air cushioning.",
            price=110.00,
            stock=100,
            created_by=1,
            images="https://example.com/nike-af1.jpg"
        )
        db.add(p)
        await db.commit()
        await db.refresh(p)

        # Seed product sizes
        for size in [8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0]:
            ps = ProductSize(product_id=p.product_id, size=size, stock=15)
            db.add(ps)
        await db.commit()

        print(f"Seeded product ID {p.product_id} successfully!")
        return p.product_id

if __name__ == "__main__":
    asyncio.run(seed_products())

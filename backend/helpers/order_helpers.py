from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.order import Order
from backend.models.order_items import OrderItem
from backend.models.products import Product
from backend.models.product_sizes import ProductSize
from backend.models.users import User


async def get_orders_all_or_404(
    user: User, 
    db: AsyncSession
) -> list[Order]:
    orders = (
        await db.execute(
            select(Order)
            .where(Order.user_id == user.id)
            .options(selectinload(Order.order_items))
        )
    ).scalars().all()

    if not orders:
        raise HTTPException(
            status_code=404,
            detail="Orders not found"
        )
    return orders


async def get_order_one_or_404(
    order_id: int,
    user: User, 
    db: AsyncSession
) -> Order:
    order = (
        await db.execute(
            select(Order)
            .where(Order.order_id == order_id, Order.user_id == user.id)
            .options(
                selectinload(Order.order_items),
                selectinload(Order.reservation)
            )
        )
    ).scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Orders not found"
        )
    return order


async def restore_stock(order: Order, db: AsyncSession):
    """Restore inventory for an expired or cancelled order in bulk without N+1 queries."""
    items = order.order_items if (hasattr(order, "order_items") and order.order_items is not None) else None
    if items is None:
        items_stmt = select(OrderItem).where(OrderItem.order_id == order.order_id)
        items = (await db.execute(items_stmt)).scalars().all()

    if not items:
        return

    product_ids = list({item.product_id for item in items})

    # Batch fetch all products
    products_stmt = select(Product).where(Product.product_id.in_(product_ids))
    products = (await db.execute(products_stmt)).scalars().all()
    product_map = {p.product_id: p for p in products}

    # Batch fetch all product sizes for sized items
    sized_items = [item for item in items if item.size]
    size_map = {}
    if sized_items:
        sizes_stmt = select(ProductSize).where(ProductSize.product_id.in_(product_ids))
        sizes = (await db.execute(sizes_stmt)).scalars().all()
        size_map = {(s.product_id, s.size): s for s in sizes}

    for item in items:
        product = product_map.get(item.product_id)
        if product:
            product.stock += item.quantity

        if item.size:
            product_size = size_map.get((item.product_id, item.size))
            if product_size:
                product_size.stock += item.quantity

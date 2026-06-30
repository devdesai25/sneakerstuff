from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from backend.models.users import User
from backend.models.cart_items import CartItem
from backend.models.order import Order
from backend.models.order_items import OrderItem
from backend.models.products import Product
from backend.schemas.orders import OrderResponse, OrderRequest
from backend.enums.order_status import OrderStatus
from backend.helpers.order_helpers import get_order_one_or_404, get_orders_all_or_404

async def restore_stock(order: Order, db: AsyncSession):

    for item in order.order_items:
        product = (
            await db.execute(
                select(Product).where(Product.product_id == item.product_id)
            )
        ).scalar_one_or_none() 
        if product:
            product.stock += item.quantity

async def orderGet(
    user: User, 
    db: AsyncSession
) -> OrderResponse:

    orders = await get_orders_all_or_404(user, db)

    return orders

async def orderCreate(
    address: OrderRequest, 
    user: User, 
    db: AsyncSession
) -> OrderResponse:

    cart = (
        await db.execute(
            select(CartItem).where(CartItem.user_id == user.id)
        )
    ).scalars().all()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    try:

        total_amount = 0
        products = {}

        for cart_item in cart:

            product = (
                await db.execute(
                    select(Product)
                    .where(Product.product_id == cart_item.product_id)
                    .with_for_update()
                )
            ).scalar_one_or_none()
            
            if not product:
                raise HTTPException(
                    status_code=404,
                    detail="Product not found"
                )

            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=422,
                    detail="Insufficient stock"
                )

            subtotal = product.price * cart_item.quantity

            total_amount += subtotal
            product.stock -= cart_item.quantity

            products[cart_item.product_id] = product

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        new_order = Order(
            user_id=user.id,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
            expires_at=expires_at,
            address=address.address
        )

        db.add(new_order)
        await db.flush()

        for cart_item in cart:

            product = products[cart_item.product_id]

            subtotal = cart_item.quantity * product.price

            order_item = OrderItem(
                order_id=new_order.order_id,
                product_id=product.product_id,
                quantity=cart_item.quantity,
                unit_price=product.price,
                subtotal=subtotal
            )

            db.add(order_item)

        await db.commit()
        await db.refresh(new_order)

    except HTTPException:
        await db.rollback()
        raise

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database integrity error"
        )

    except Exception:
        await db.rollback()
        raise

    return new_order

async def orderPay(
    order_id: int, 
    user: User, 
    db: AsyncSession
) -> OrderResponse:

    order = await get_order_one_or_404(order_id, user, db)
    
    if (
        order.status == OrderStatus.PENDING 
        and datetime.now(timezone.utc) > order.expires_at
    ):  
        await restore_stock(order, db)
        order.status = OrderStatus.EXPIRED
        await db.commit()

    if order.status == OrderStatus.EXPIRED:
        raise HTTPException(
            status_code=400,
            detail="Order has Expired"
        )

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=422,
            detail="Unprocessable entity"
        )

    try:
        order.status = OrderStatus.PAID
        order.paid_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(order)


    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database integrity error"
        )
    
    except Exception:
        await db.rollback()
        raise

    return order

async def orderCancel(
    order_id: int, 
    user: User, 
    db: AsyncSession
) -> OrderResponse:

    order = await get_order_one_or_404(order_id, user, db)

    if (datetime.now(timezone.utc) > order.expires_at
        and order.status == OrderStatus.PENDING
    ):
        await restore_stock(order, db)

        order.status = OrderStatus.EXPIRED
        await db.commit()

    if order.status == OrderStatus.EXPIRED:
        raise HTTPException(
            status_code=400,
            detail="Order has Expired"
        )

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=422,
            detail="Unprocessable entity"
        )
    
    try:
        await restore_stock(order, db)
        order.status = OrderStatus.CANCELLED

        await db.commit()
        await db.refresh(order)
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database integrity error"
        )
    
    except Exception:
        await db.rollback()
        raise
    
    return order
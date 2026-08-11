from fastapi import HTTPException
from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from backend.models.users import User
from backend.models.cart_items import CartItem
from backend.models.order import Order
from backend.models.order_items import OrderItem
from backend.models.products import Product
from backend.models.product_sizes import ProductSize
from backend.schemas.orders import OrderResponse, OrderRequest
from backend.enums.order_status import OrderStatus
from backend.helpers.order_helpers import get_order_one_or_404, get_orders_all_or_404, restore_stock
from backend.tasks.drop_tasks import expire_unpaid_reservations

async def order_get(
    user: User, 
    db: AsyncSession
) -> OrderResponse:

    orders = await get_orders_all_or_404(user, db)

    return orders

async def order_create(
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

            if product.is_reserved_for_drop:
                raise HTTPException(
                    status_code=400,
                    detail="This sneaker is reserved for an upcoming drop and cannot be ordered directly"
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
                subtotal=subtotal,
                size=cart_item.size
            )

            db.add(order_item)

        await db.commit()
        await db.refresh(new_order)

        stmt = (
        select(Order)
            .where(Order.order_id == new_order.order_id)
            .options(
                selectinload(Order.order_items),
                selectinload(Order.user),
            )
        )

        result = await db.execute(stmt)
        new_order = result.scalar_one()

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

async def order_pay(
    order_id: int, 
    user: User, 
    db: AsyncSession
) -> OrderResponse:

    order = await get_order_one_or_404(order_id, user, db)

    from backend.models.reservations import Reservation
    reservation = (
        await db.execute(
            select(Reservation)
            .where(Reservation.order_id == order.order_id)
            .options(selectinload(Reservation.entry))
        )
    ).scalar_one_or_none()

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=422,
            detail="Unprocessable entity"
        )
    
    now = datetime.now(timezone.utc)
    expires_at = order.expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at and now > expires_at:
        if not reservation:
            await restore_stock(order, db)
        else:
            from backend.models.drops import Drop
            from backend.tasks.drop_tasks import _check_and_complete_drop
            if reservation.entry:
                drop = (
                    await db.execute(
                        select(Drop).where(Drop.drop_id == reservation.entry.drop_id).with_for_update()
                    )
                ).scalar_one_or_none()
                if drop:
                    drop.drop_inventory += 1
                    await _check_and_complete_drop(drop, db)

        order.status = OrderStatus.EXPIRED
        await db.commit()

        raise HTTPException(
            status_code=400,
            detail="Order has expired"
        )

    try:
        order.status = OrderStatus.PAID
        order.paid_at = now

        for item in order.order_items:
            if item.size:
                p_size = (
                    await db.execute(
                        select(ProductSize).where(
                            ProductSize.product_id == item.product_id,
                            ProductSize.size == item.size
                        ).with_for_update()
                    )
                ).scalar_one_or_none()
                if p_size and p_size.stock > 0:
                    p_size.stock = max(0, p_size.stock - item.quantity)

        # Check if this order is linked to a drop reservation and auto-complete the drop if all entries/reservations are settled
        from backend.models.drops import Drop
        from backend.tasks.drop_tasks import _check_and_complete_drop

        if reservation and reservation.entry:
            drop = (
                await db.execute(
                    select(Drop).where(Drop.drop_id == reservation.entry.drop_id)
                )
            ).scalar_one_or_none()
            if drop:
                await _check_and_complete_drop(drop, db)

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

async def order_cancel(
    order_id: int, 
    user: User, 
    db: AsyncSession
) -> OrderResponse:

    order = (
        await db.execute(
            select(Order)
            .where(Order.order_id == order_id, Order.user_id == user.id)
            .options(selectinload(Order.reservation))
        )
    ).scalar_one_or_none() 

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

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
    
    is_raffle_order = order.reservation is not None
    now = datetime.now(timezone.utc)
    expires_at = order.expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at and now > expires_at:
        if not is_raffle_order:
            await restore_stock(order, db)

        order.status = OrderStatus.EXPIRED
        await db.commit()
        await db.refresh(order)
        
        raise HTTPException(
            status_code=400,
            detail="Order has expired"
        )

    try:
        if not is_raffle_order:
            await restore_stock(order, db)
        
        order.status = OrderStatus.CANCELLED

        if is_raffle_order and order.reservation:
            from backend.models.entry import Entry
            from backend.models.reservations import Reservation
            from backend.models.drops import Drop
            from backend.tasks.drop_tasks import _check_and_complete_drop

            res_entry_id = order.reservation.entry_id

            entry = (
                await db.execute(
                    select(Entry).where(Entry.entry_id == res_entry_id)
                )
            ).scalar_one_or_none()

            if entry:
                drop = (
                    await db.execute(
                        select(Drop).where(Drop.drop_id == entry.drop_id)
                    )
                ).scalar_one_or_none()

                if drop:
                    drop.drop_inventory += 1

                    next_entry_stmt = (
                        select(Entry)
                        .where(
                            Entry.drop_id == drop.drop_id,
                            ~exists().where(Reservation.entry_id == Entry.entry_id)
                        )
                        .order_by(Entry.ranking.asc())
                        .limit(1)
                    )
                    next_winner = (await db.execute(next_entry_stmt)).scalar_one_or_none()

                    if next_winner:
                        drop.drop_inventory -= 1
                        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
                        new_order = Order(
                            user_id=next_winner.user_id,
                            total_amount=drop.product_price,
                            status=OrderStatus.PENDING,
                            expires_at=expires_at,
                            address=next_winner.address
                        )
                        db.add(new_order)
                        await db.flush()

                        new_order_item = OrderItem(
                            order_id=new_order.order_id,
                            product_id=drop.product_id,
                            quantity=1,
                            unit_price=drop.product_price,
                            subtotal=drop.product_price,
                            size=next_winner.size
                        )
                        db.add(new_order_item)

                        new_res = Reservation(
                            entry_id=next_winner.entry_id,
                            order_id=new_order.order_id
                        )
                        db.add(new_res)
                        await db.flush()
                    else:
                        await _check_and_complete_drop(drop, db)

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
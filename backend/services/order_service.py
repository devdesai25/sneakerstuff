from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from models.cart_items import CartItem
from models.order import Order
from models.order_items import OrderItem
from models.products import Product
from datetime import datetime, timedelta


def orderGet(user, db):

    orders = (
        db.query(Order)
        .filter(Order.user_id == user.id)
        .all()
    )

    if not orders:
        raise HTTPException(
            status_code=404,
            detail="Orders not found"
        )

    return {
        "orders": [
            {
                "order_id": order.order_id,
                "status": order.status,
                "address": order.address,
                "total_amount": order.total_amount,
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "subtotal": item.subtotal
                    }
                    for item in order.order_items
                ]
            }
            for order in orders
        ]
    }


def orderCreate(address, user, db):

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    cart = (
        db.query(CartItem)
        .filter(CartItem.user_id == user.id)
        .all()
    )

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
                db.query(Product)
                .filter(Product.product_id == cart_item.product_id)
                .first()
            )

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail="Product not found"
                )

            if product.quantity < cart_item.quantity:
                raise HTTPException(
                    status_code=422,
                    detail="Insufficient stock"
                )

            subtotal = product.price * cart_item.quantity

            total_amount += subtotal
            product.quantity -= cart_item.quantity

            products[cart_item.product_id] = product

        expires_at = datetime.utcnow() + timedelta(minutes=10)

        new_order = Order(
            user_id=user.id,
            total_amount=total_amount,
            status="Pending",
            expires_at=expires_at,
            address=address.address
        )

        db.add(new_order)
        db.flush()

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

        db.commit()
        db.refresh(new_order)

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database integrity error"
        )

    except Exception:
        db.rollback()
        raise

    return {
        "order_id": new_order.order_id,
        "total_amount": new_order.total_amount,
        "status": new_order.status,
        "expires_at": new_order.expires_at,
        "address": new_order.address,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.subtotal
            }
            for item in new_order.order_items
        ]
    }
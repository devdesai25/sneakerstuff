from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
from backend.models.cart_items import CartItem
from backend.models.order import Order
from backend.models.order_items import OrderItem
from backend.models.products import Product

def restore_stock(order, db):

    for item in order.order_items:

        product = (
            db.query(Product)
            .filter(Product.product_id == item.product_id)
            .first()
        )

        product.stock += item.quantity

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

            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=422,
                    detail="Insufficient stock"
                )

            subtotal = product.price * cart_item.quantity

            total_amount += subtotal
            product.stock -= cart_item.quantity

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

def orderPay(id, user, db):

    order = (
        db.query(Order)
        .filter(Order.order_id == id, Order.user_id == user.id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order Not found"
        )
    
    if (
        order.status == "Pending" 
        and datetime.now(timezone.utc) > order.expires_at
    ):  
        restore_stock(order, db)
        order.status = "Expired"
        db.commit()

    if order.status == "Expired":
        raise HTTPException(
            status_code=400,
            detail="Order has Expired"
        )

    if order.status != "Pending":
        raise HTTPException(
            status_code=422,
            detail="Unprocessable entity"
        )

    try:
        order.status = "Paid"
        order.paid_at = datetime.utcnow()

        db.commit()
        db.refresh(order)


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
        "order_id":order.order_id,
        "status":order.status,
        "paid_at":order.paid_at,
        "amount":order.total_amount, 
        "address":order.address
    }

def orderCancel(id, user, db):

    order = (
        db.query(Order)
        .filter(Order.order_id == id, Order.user_id == user.id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order Not Found"
        )

    if (datetime.now(timezone.utc) > order.expires_at
        and order.status == "Pending"
    ):
        restore_stock(order, db)

        order.status = "Expired"
        db.commit()

    if order.status == "Expired":
        raise HTTPException(
            status_code=400,
            detail="Order has Expired"
        )

    if order.status != "Pending":
        raise HTTPException(
            status_code=422,
            detail="Unprocessable entity"
        )
    
    try:
        restore_stock(order, db)
        order.status = "Cancelled"

        db.commit()
        db.refresh(order)
    
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
        "order_id":order.order_id,
        "status":order.status,
        "amount":order.total_amount,
        "address":order.address 
    }
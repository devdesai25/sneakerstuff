from fastapi import HTTPException
from models.products import Product
from models.cart_items import CartItem
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

def cartAdd(
        cur_cart,
        user, 
        db
    ):
    """Add to cart with validation"""
    product = (
        db.get(Product, 
        cur_cart.product_id)
        )

    if product is None:
        raise HTTPException(
            status_code= 404,
            detail= "Product Not found"
        )
    """Check Available quantity before creating cart"""
    if product.stock < cur_cart.quantity:
        raise HTTPException(
            status_code= 409,
            detail="Product is out of stock"
        )
    
    cart = (
        db.query(CartItem)
        .filter(CartItem.user_id == user.id, CartItem.product_id == cur_cart.product_id)
        .first()
    )

    
    if cart is None:
        try:
            add_to_cart = CartItem(
                user_id = user.id,
                product_id = cur_cart.product_id,
                quantity = cur_cart.quantity
            )

            db.add(add_to_cart)
            db.commit()
            db.refresh(add_to_cart)

            return add_to_cart

        except IntegrityError:
            db.rollback()
            
            raise HTTPException(
                status_code=409,
                detail="Database Integrity Error"
            )
        
    if product.stock < (cur_cart.quantity + cart.quantity):
       raise HTTPException(
           status_code=409,
           detail = "Stock unavailable"
       ) 
   
    try:
        cart.quantity += cur_cart.quantity
        db.commit()
        db.refresh(cart)
    
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Database integrity error"
        )

    return cart

def cartPatch(
        id, 
        cur_cart, 
        user, 
        db
    ):
    """Set/Delete Product from cart"""
    product = (
        db.query(Product)
        .filter(Product.product_id == id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code= 404,
            detail= "Product Not Found"
        )
    
    cart = (
        db.query(CartItem)
        .filter(CartItem.user_id == user.id, CartItem.product_id == id)
        .first()
    )

    if cart is None:
        raise HTTPException(
            status_code= 404,
            detail= "Cart Not Found"
        )

    if product.stock < cart.quantity:
        raise HTTPException(
            status_code= 409,
            detail= "Product Out of Stock"
        )
    
    try:
        if cur_cart.quantity == 0:
            db.delete(cart)
            db.commit()
            return {"Message": "Product Removed From Cart"}
        
        else:
            cart.quantity = cur_cart.quantity
            db.commit()
            db.refresh(cart)

            return cart
    
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code= 409,
            detail= "Database Integrity Error"
        )

def cartDelete(
        id, 
        user, 
        db
    ):
    """Delete Product from Cart"""
    cart = (
        db.query(CartItem)
        .filter(CartItem.user_id == user.id, CartItem.product_id == id)
        .first()
    )

    if cart is None:
        raise HTTPException(
            status_code= 404,
            detail= "Cart Not Found"
        )
    
    try:
        db.delete(cart)
        db.commit()
    
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code= 409,
            detail= "Database Integrity Error"
        )
    
    return {"Message": "Product Deleted From Cart Successfully"}
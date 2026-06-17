from fastapi import Depends, HTTPException
from models.products import Product
from models.users import User
from sqlalchemy.exc import IntegrityError

def productadd(cur_product, admin,db):
    """Create a new product with duplicate check"""
    product = (
        db.query(Product)
        .filter(Product.name == cur_product.name)
        .first()
    )

    if product :
        raise HTTPException(
            status_code=409,
            detail="Duplicate Value Inserted"
        )

    add_prod = Product(
        name = cur_product.name, 
        description = cur_product.description, 
        price = cur_product.price, 
        stock = cur_product.stock, 
        created_by = admin.id,
        images = cur_product.images
    ) 
    
    try:
        db.add(add_prod)
        db.commit()
        db.refresh(add_prod)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            409,
            detail="Database Integrity Error"
        )
    
    return add_prod

def productDelete(id: int, db):
    """Delete a product"""
    product = (
        db.get(Product, id)
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product Not Found"
        )
    
    try:
        db.delete(product)
        db.commit()

    except IntegrityError:
        db.rollback()
        
        raise HTTPException(
            status_code=409,
            detail="Database Integrity Error"
        )
    
    return {
        "message": "Product deleted successfully"
    }

def productUpdate(id: int, update_product, db):
    """Update a product"""
    product = (
        db.get(Product, id)
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product Not Found"
        )
    
    """Skip fields client hasnt sent"""
    """Convert Pydantic model to dict, only with fields client sent"""
    update_data = update_product.model_dump(exclude_unset=True)

    for key, value in update_data().items():
        if hasattr(product, key):
            setattr(product, key, value)
    
    try:
        db.commit()
        db.refresh(product)
    
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Database Integrity Error"
        )
    
    return {
        "message": "Product Updated Successfully"
    }
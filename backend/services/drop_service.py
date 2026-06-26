from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from backend.models.drops import Drop
from backend.models.products import Product

def dropGet(db):
    drop = db.query(Drop).all()
    
    return drop


def dropCreate(drop, db):

    product = (
        db.query(Product)
        .filter(Product.product_id == drop.product_id)
        .first()
    )    

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product Not Found"
        )
    
    if product.stock < drop.drop_inventory:
        raise HTTPException(
            status_code=422,
            detail="Infsufficient Stock"
        )
    
    if (drop.closes_at < drop.opens_at
        or drop.opens_at >drop.closes_at
    ) :
        raise HTTPException(
            status_code=422,
            detail="Unprocessable Entity"
        )
    
    try:
        new_drop = Drop(
            product_id = drop.product_id,
            opens_at = drop.opens_at,
            closes_at = drop.closes_at,
            drop_inventory = drop.drop_inventory,
            status = "DRAFT"
        )
        db.add(new_drop)
        db.commit()
        db.refresh(new_drop)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database Integrity Error"
        )
    
    except Exception:
        db.rollback()
        raise

    return {
       "drop_id": new_drop.drop_id,
       "product_id": new_drop.product_id,
       "product_name": new_drop.product.name,
       "status": new_drop.status,
       "opens_at": new_drop.opens_at,
       "closes_at": new_drop.closes_at,
       "created_at": new_drop.created_at,
       "drop_inventory": new_drop.drop_inventory 
    }
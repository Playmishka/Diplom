from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from DB import get_session
from auth.jwt_auth import get_current_auth_user
from models.modelsDB import product, storehouse
from models.modelsData import ProductModel, UserSchema

router = APIRouter(prefix="/products", tags=["Products"], dependencies=[Depends(get_current_auth_user)])


@router.get("/get_all", response_model=List[ProductModel])
def get_products(session: Session = Depends(get_session)):
    return session.query(product).all()


@router.get("/add_new")
def add_product(product_name: str,
                session: Session = Depends(get_session)):
    # Проверяем, существует ли уже такой продукт
    existing_product = session.execute(select(product).where(product.c.name == product_name.title())).fetchone()

    if existing_product:
        return {"message": f"Product {product_name.title()} already exists."}
    else:
        try:
            session.execute(insert(product).values(name=product_name.title()))
            session.commit()
            return {"message": f"Product {product_name.title()} added."}
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=500, detail="Failed to add product due to integrity error")
        except Exception:
            session.rollback()
            raise HTTPException(status_code=500, detail="Failed to add product")


@router.put("/spend_items/{product_id}")
def spend_items(product_id: int, count: int, session: Session = Depends(get_session)):
    stmt = select(storehouse).filter(storehouse.c.id == product_id)
    store_item = session.execute(stmt).fetchone()

    if not store_item:
        raise HTTPException(status_code=404, detail="Product not found")

    current_count = store_item.count

    if current_count < count:
        raise HTTPException(status_code=400, detail="Not enough items in stock")

    updated_count = current_count - count

    stmt = update(storehouse).where(storehouse.c.id == product_id).values(count=updated_count)
    session.execute(stmt)
    session.commit()

    return {"message": f"Succesfully spent {count} items of product {product_id}"}
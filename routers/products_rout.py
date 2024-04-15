from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from DB import get_session
from auth.jwt_auth import get_current_auth_user
from models.modelsDB import product
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

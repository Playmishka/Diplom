import json
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from models.modelsData import ProductModel, RequestProducts, Status
from config import DB_PATH
from models.modelsDB import product, main_storehouse, storehouse, request

app = FastAPI()

engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()


# Получение всех товаров.
@app.get("/products/", response_model=List[ProductModel])
def get_products(session: Session = Depends(get_session)):
    return session.query(product).all()


@app.get("/add_product/")
def add_product(product_name: str, session: Session = Depends(get_session)):
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


@app.get("/add_product_main_storehouse/")
def add_product_main_storehouse(product_id: int, count: int, session: Session = Depends(get_session)):
    try:
        name_product = session.execute(select(product).where(product.c.id == product_id)).fetchone().name
        existing_entry = (session.execute(select(main_storehouse).where(main_storehouse.c.product == product_id))
                          .fetchone())
        if not existing_entry:
            session.execute(insert(main_storehouse).values(product=product_id, count=count))
            session.commit()
            return {"message": f"Product {name_product} added."}
        else:
            session.execute(update(main_storehouse).where(main_storehouse.c.product == product_id).values(
                count=main_storehouse.c.count + count
            ))
            session.commit()
            return {"message": f"Product {name_product} updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update main storehouse")


@app.get("/add_product_storehouse/")
def add_product_storehouse(product_id: int, count: int, session: Session = Depends(get_session)):
    try:
        name_product = session.execute(select(product).where(product.c.id == product_id)).fetchone().name
        main_storehouse_entry = (session.execute(select(main_storehouse).where(main_storehouse.c.product == product_id))
                                 .fetchone())
        if not main_storehouse_entry:
            return {"message": f"Product {name_product} not found."}
        elif main_storehouse_entry.count < count:
            return {"message": f"Insufficient stock for Product {name_product}."}
        else:
            storehouse_entry = session.execute(select(storehouse).where(storehouse.c.product == product_id)).fetchone()
            if not storehouse_entry:
                session.execute(insert(storehouse).values(product=product_id, count=count))
            else:
                session.execute(update(storehouse).where(storehouse.c.product == product_id).values(
                    count=storehouse.c.count + count
                ))
            session.execute(update(main_storehouse).where(main_storehouse.c.product == product_id).values(
                count=main_storehouse.c.count - count
            ))
            session.commit()
            return {"message": f"Added {count} units of Product {name_product} to storehouse."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update storehouse")


@app.post("/add_request/")
def create_request(request_item: RequestProducts, status: Status, session: Session = Depends(get_session)):
    try:
        products_data = [{"product_id": item.product_id, "count": item.count} for item in request_item.list_products]
        products_json = json.dumps(products_data)
        new_request = {"products": products_json, "status": status.value, "date": datetime.utcnow()}
        session.execute(insert(request).values(**new_request))
        session.commit()
        return {"message": "Request added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to add request")
from typing import List

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import sessionmaker
from models.modelsData import ProductModel
from config import DB_PATH
from models.modelsDB import product, main_storehouse, storehouse

app = FastAPI()

engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()


# Запрос на получение всех продуктов.
@app.get("/products/", response_model=List[ProductModel])
def get_products(session: Session = Depends(get_session)):
    return session.query(product).all()


# Запрос на добавление продукта.
@app.get("/add_product/")
def add_product(product_name: str, session: Session = Depends(get_session)):
    session.execute(insert(product).values(name=product_name))
    session.commit()
    return [{"message": f"Product {product_name} added."}]


@app.get("/add_product_main_storehouse/")
def add_product_storehouse(product_name: int, count: int, session: Session = Depends(get_session)):
    select_stmt = select(main_storehouse).where(main_storehouse.c.product == product_name)
    result = session.execute(select_stmt)
    entry = result.fetchone()
    if entry is None:
        session.execute(insert(main_storehouse).values(product=product_name, count=count))
        session.commit()
        return {"message": f"Product {product_name} added."}
    else:
        update_stmt = main_storehouse.update().where(main_storehouse.c.product == product_name).values(
            count=main_storehouse.c.count + count
        )
        session.execute(update_stmt)
        session.commit()
        return {"message": f"Product {product_name} updated."}


@app.get("/add_product_storehouse/")
def add_product_storehouse(product_id: int, count: int, session: Session = Depends(get_session)):
    select_stmt = select(main_storehouse).where(main_storehouse.c.product == product_id)
    result = session.execute(select_stmt)
    entry = result.fetchone()
    if entry is None:
        return {"message": f"Product {product_id} not found."}
    elif entry.count < count:
        return {"message": f"Product {product_id} count none."}
    else:
        select_stmt = select(storehouse).where(storehouse.c.product == product_id)
        result = session.execute(select_stmt)
        entry = result.fetchone()
        if entry is None:
            stmt = insert(storehouse).values(product=product_id, count=count)
            session.execute(stmt)
            session.commit()
        else:
            stmt = storehouse.update().where(storehouse.c.product == product_id).values(
                count=storehouse.c.count + count)
            session.execute(stmt)
            session.commit()
        update_stmt = main_storehouse.update().where(main_storehouse.c.product == product_id).values(
            count=main_storehouse.c.count - count
        )
        session.execute(update_stmt)
        session.commit()
    return {"message": f"Product {product_id} added, count {count}."}

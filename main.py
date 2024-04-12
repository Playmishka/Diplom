import json
from collections import defaultdict
from datetime import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from models.modelsData import ProductModel, RequestProducts, Status, RequestOutputModel, RequestProduct, \
    RequestProductsOutputModel
from config import DB_PATH
from models.modelsDB import product, main_storehouse, storehouse, request, product_per_request

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
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update main storehouse")


@app.get("/add_product_storehouse/")
def add_product_storehouse(product_id: int, count: int, session: Session = Depends(get_session)):
    try:
        name_product = session.execute(select(product).where(product.c.id == product_id)).fetchone().name
        existing_entry = (session.execute(select(main_storehouse).where(main_storehouse.c.product == product_id))
                          .fetchone())
        if not existing_entry:
            return {"message": f"Product {name_product} not found."}
        elif existing_entry.count < count:
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
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update storehouse")


@app.post("/add_request/")
def create_request(request_item: RequestProducts, status: Status, session: Session = Depends(get_session)):
    try:
        # Создание запроса
        new_request = session.execute(insert(request).values(status=status.value))
        new_request_id = new_request.inserted_primary_key[0]

        # Добавление продуктов в запрос
        products_data = [{"product_id": item.product_id, "count": item.count} for item in
                         request_item.list_products]
        for item in products_data:
            session.execute(insert(product_per_request).values(request_id=new_request_id,
                                                               product=item.get("product_id"),
                                                               count=item.get("count")))
        session.commit()

        return {"message": f"Request {new_request_id} added."}
    except IntegrityError:
        return {"error": "Integrity error occurred. Please check your input data."}


# @app.get("/get_requests/", response_model=List[RequestOutputModel])
# def get_requests(session: Session = Depends(get_session)):
#     try:
#         stmt = select(request.c.id, request.c.data, request.c.status,
#                       product_per_request.c.product, product_per_request.c.count,
#                       product.c.name) \
#             .select_from(
#             request.join(product_per_request).join(product))  # Joining request, product_per_request, and product
#
#         result = session.execute(stmt)
#         requests_dict = {}
#         for row in result:
#             request_id, request_data, request_status, product_id, product_count, product_name = row
#             if request_id not in requests_dict:
#                 requests_dict[request_id] = {
#                     "id": request_id,
#                     "products": [],
#                     "status": request_status,
#                     "date": request_data
#                 }
#             requests_dict[request_id]["products"].append(
#                 RequestProductsOutputModel(name=product_name, count=product_count)
#             )
#
#         # Converting dictionary values to list of RequestOutputModel
#         requests = [RequestOutputModel(**req_data) for req_data in requests_dict.values()]
#         return requests
#     except SQLAlchemyError as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/get_requests/", response_model=List[RequestOutputModel])
def get_requests(session: Session = Depends(get_session)):
    try:
        stmt = select(request.c.id, request.c.data, request.c.status,
                      product_per_request.c.product, product_per_request.c.count,
                      product.c.name) \
            .select_from(
            request.join(product_per_request).join(product))  # Joining request, product_per_request, and product

        result = session.execute(stmt)
        requests_dict = defaultdict(lambda: {"id": 0, "products": [], "status": "", "date": datetime.now()})
        for row in result.fetchall():
            request_id, request_data, request_status, product_id, product_count, product_name = row
            requests_dict[request_id]["id"] = request_id
            requests_dict[request_id]["status"] = request_status
            requests_dict[request_id]["date"] = request_data
            requests_dict[request_id]["products"].append(
                RequestProductsOutputModel(name=product_name, count=product_count)
            )

        # Converting dictionary values to list of RequestOutputModel
        requests = [RequestOutputModel(**req_data) for req_data in requests_dict.values()]
        return requests
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
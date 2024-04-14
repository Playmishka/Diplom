from collections import defaultdict
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from DB import get_session
from models.modelsDB import request, product_per_request, product
from models.modelsData import RequestProducts, RequestOutputModel, RequestProductsOutputModel, Status
import requests

router = APIRouter(prefix="/requests")




@router.post("/create_request/")
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


@router.get("/get_all", response_model=List[RequestOutputModel])
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


@router.get("/get_processing", response_model=List[RequestOutputModel])
def get_processing_requests(session: Session = Depends(get_session)):
    try:
        stmt = select(request.c.id, request.c.data, request.c.status,
                      product_per_request.c.product, product_per_request.c.count,
                      product.c.name) \
            .select_from(
            request.join(product_per_request).join(product)) \
            .where(request.c.status == Status.PROCESSING.value)

        result = session.execute(stmt)
        requests_dict = {}
        for row in result.fetchall():
            request_id, request_data, request_status, product_id, product_count, product_name = row
            if request_id not in requests_dict:
                requests_dict[request_id] = {
                    "id": request_id,
                    "products": [],
                    "status": request_status,
                    "date": request_data
                }
            requests_dict[request_id]["products"].append(
                RequestProductsOutputModel(name=product_name, count=product_count)
            )

        # Converting dictionary values to list of RequestOutputModel
        requests = [RequestOutputModel(**req_data) for req_data in requests_dict.values()]
        return requests
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/perform_request")
def perform_request(request_id: int, session: Session = Depends(get_session)):
    products = session.execute(select(product_per_request).filter(product_per_request.c.request_id == request_id)).all()
    for item in products:
        requests.get(f"http://127.0.0.1:8000/add_products/storehouse?product_id={item.product}&count={item.count}")

    session.execute(update(request).where(request.c.id == request_id).values(status=Status.COMPLETED.value))
    session.commit()


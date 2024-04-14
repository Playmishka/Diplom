from typing import List

from fastapi import APIRouter, Depends
from DB import get_session, Session
from models.modelsDB import product, storehouse, main_storehouse
from models.modelsData import Storehouse_get

router = APIRouter(prefix="/storehouse")


def get_storehouse_data(session: Session, storehouse_table):
    storehouse_data = session.query(storehouse_table).all()

    list_products = []

    for data in storehouse_data:
        product_name = session.query(product.c.name).filter(product.c.id == data.product).scalar()

        storehouse_item = {
            "id": data.id,
            "name": product_name,
            "count": data.count
        }
        list_products.append(storehouse_item)

    return list_products


@router.get("/main_storehouse", response_model=List[Storehouse_get])
def get_main_storehouse(session: Session = Depends(get_session)):
    return get_storehouse_data(session, main_storehouse)


@router.get("/storehouse", response_model=List[Storehouse_get])
def get_storehouse(session: Session = Depends(get_session)):
    return get_storehouse_data(session, storehouse)

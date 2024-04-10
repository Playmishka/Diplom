import enum
from typing import List
from pydantic import BaseModel, Field


class ProductModel(BaseModel):
    id: int = Field(gt=0)
    name: str


class RequestProduct(BaseModel):
    product_id: int = Field(gt=0)
    count: int = Field(gt=0)


class RequestProducts(BaseModel):
    list_products: List[RequestProduct]


class Status(enum.Enum):
    PROCESSING = 'В процессе'
    COMPLETED = 'Выполнена'

import enum
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class Status(enum.Enum):
    PROCESSING = 'В процессе'
    COMPLETED = 'Выполнена'


class ProductModel(BaseModel):
    id: int = Field(gt=0)
    name: str


class RequestProduct(BaseModel):
    product_id: int = Field(gt=0)
    count: int = Field(gt=0)


class RequestProducts(BaseModel):
    list_products: List[RequestProduct]


class RequestProductsOutputModel(BaseModel):
    name: str = Field()
    count: int = Field(gt=0)


class RequestOutputModel(BaseModel):
    products: List[RequestProductsOutputModel]
    status: str = Field(Status)
    date: datetime

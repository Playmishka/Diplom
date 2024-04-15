import enum
from datetime import datetime
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field, ConfigDict

BASE_DIR = Path(__file__).parent.parent


class Status(enum.Enum):
    PROCESSING = 'В процессе'
    COMPLETED = 'Выполнен'


class Storehouse_get(BaseModel):
    id: int
    name: str
    count: int


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
    id: int
    products: List[RequestProductsOutputModel]
    status: str = Field(Status)
    date: datetime


class Auth_JWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "public.pem"
    algorithm: str = Field(default="RS256")
    access_token_exp_minutes: int = 15


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    username: str
    password: bytes

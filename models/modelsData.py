from pydantic import BaseModel


class ProductModel(BaseModel):
    id: int
    name: str

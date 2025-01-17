from datetime import datetime
from sqlalchemy import MetaData, Integer, String, Column, TIMESTAMP, ForeignKey, Table

from models.modelsData import Status

metadata = MetaData()


def getDateTime():
    return datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S")


# Таблица всех продуктов.
product = Table(
    "product",  # Название таблицы
    metadata,  # Подключаем метаданные
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
)

# Таблица главного склада.
main_storehouse = Table(
    "main_storehouse",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("product", Integer, ForeignKey("product.id"), nullable=False),
    Column("count", Integer, nullable=False),
)

# Таблица склада точки.
storehouse = Table(
    "storehouse",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("product", Integer, ForeignKey("product.id"), nullable=False),
    Column("count", Integer, nullable=False),
)

product_per_request = Table(
    "product_per_request",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("request_id", Integer, ForeignKey("request.id"), nullable=False),
    Column("product", Integer, ForeignKey("product.id"), nullable=False),
    Column("count", Integer, nullable=False),
)

request: Table = Table(
    "request",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("data", TIMESTAMP, nullable=False, default=getDateTime),
    Column("status", String, nullable=False, default=Status.PROCESSING)
)

# Таблица пользователей.
user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False),
    Column("password", String, nullable=False),
)

from datetime import datetime
from sqlalchemy import MetaData, Integer, String, Column, TIMESTAMP, ForeignKey, Table, JSON

from models.modelsData import Status

metadata = MetaData()
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

# Таблица заявки
request = Table(
    "request",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("products", JSON, nullable=False),
    Column("date", TIMESTAMP, default=datetime.utcnow),
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

from fastapi import FastAPI
from routers.products import router as products_router
from routers.add_products import router as add_products_router
from routers.requests import router as requests_router
from routers.storehouse import router as storehouse_router

app = FastAPI()

app.include_router(products_router)
app.include_router(add_products_router)
app.include_router(requests_router)
app.include_router(storehouse_router)

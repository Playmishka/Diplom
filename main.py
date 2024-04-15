from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.products_rout import router as products_router
from routers.add_products_rout import router as add_products_router
from routers.requests_rout import router as requests_router
from routers.storehouse_rout import router as storehouse_router
from auth.jwt_auth import router as jwt_router

app = FastAPI()

app.include_router(products_router)
app.include_router(add_products_router)
app.include_router(requests_router)
app.include_router(storehouse_router)
app.include_router(jwt_router)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

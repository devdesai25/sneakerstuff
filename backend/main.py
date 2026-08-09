from fastapi import FastAPI

from backend.routes import (
    auth_router,
    product_router,
    cart_router,
    order_router,
    drop_router,
    entry_router
)
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_headers = ["*"],
    allow_methods = ["*"]
)

app.include_router(auth_router, prefix="/api")
app.include_router(product_router, prefix="/api")
app.include_router(cart_router, prefix="/api")
app.include_router(order_router, prefix="/api")
app.include_router(drop_router, prefix="/api")
app.include_router(entry_router, prefix="/api")
handler = Mangum(app)
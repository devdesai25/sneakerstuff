from fastapi import FastAPI
from config import settings
from database import engine, Base, metadata
from routes import (
                    auth_router,
                    me_router, 
                    product_router,
                    cart_router,
                    order_router,
                )
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_headers = ["*"],
    allow_methods = ["*"]
)

app.include_router(auth_router)
app.include_router(me_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)
handler = Mangum(app)
"""
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def root():
    return {"status": "working"}

handler = Mangum(app)"""
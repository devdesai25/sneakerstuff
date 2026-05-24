from fastapi import FastAPI
from config import settings
from database import engine, Base, metadata
from routes import cart,login_router, get_products_router, signup_router, me_router, admin_router, create_product_router, delete_product_router, update_product_router, route
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

app.include_router(login_router)
app.include_router(get_products_router)
app.include_router(signup_router)
app.include_router(me_router)
app.include_router(admin_router)
app.include_router(create_product_router)
app.include_router(delete_product_router)
app.include_router(update_product_router)
app.include_router(route)
app.include_router(cart)

handler = Mangum(app)
"""
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def root():
    return {"status": "working"}

handler = Mangum(app)"""
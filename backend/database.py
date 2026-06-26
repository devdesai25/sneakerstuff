from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from backend.config import settings

metadata = MetaData()
engine  = create_engine( settings.DATABASE_URL )
class Base(DeclarativeBase):
    pass
    
sessionlocal = sessionmaker(bind = engine, autocommit=False, autoflush=False)

def get_db():
    
    db = sessionlocal()

    try:
        yield db
    finally:
        db.close()
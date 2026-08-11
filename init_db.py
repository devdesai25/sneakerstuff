import asyncio
from backend.database import Base, engine
import backend.models  # Ensures all models are registered with Base.metadata

async def init_tables():
    print("Creating all database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_tables())

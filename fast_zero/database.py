from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fast_zero.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():  # pragma: no cover
    async with SessionLocal() as session:
        yield session

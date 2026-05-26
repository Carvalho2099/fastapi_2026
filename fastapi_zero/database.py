from sqlalchemy.ext.asyncio import (
    create_async_engine as create_engine,
    AsyncSession as Session,
)

from fastapi_zero.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


async def get_session():
    async with Session(engine) as session:
        yield session

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine as create_engine,
    AsyncSession as Session,
)
from contextlib import contextmanager
from datetime import datetime
from sqlalchemy.pool import StaticPool
from sqlalchemy import event

from fastapi.testclient import TestClient
from fastapi_zero.models import table_registry, User
from fastapi_zero.app import app
from fastapi_zero.database import get_session
from fastapi_zero.security import get_password_hash


@pytest.fixture
def client(session):
    async def get_session_override():
        yield session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with Session(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(*, model, time=datetime.now()):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session: Session):
    password = 'secret'

    user = User(
        username='Test',
        email='test@test.com',
        password=get_password_hash(password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password
    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']

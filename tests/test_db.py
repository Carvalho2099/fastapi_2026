from fastapi_zero.models import User
from sqlalchemy import select
from dataclasses import asdict
from sqlalchemy.ext.asyncio import AsyncSession as Session
import pytest


@pytest.mark.asyncio
async def test_create_user(session: Session, mock_db_time):

    with mock_db_time(model=User) as time:
        new_user = User(
            username='test', email='test@test.com', password='secret'
        )

        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'test')
        )

    assert asdict(user) == {
        'id': 1,
        'username': 'test',
        'email': 'test@test.com',
        'password': 'secret',
        'created_at': time,
        'update_at': None,
    }

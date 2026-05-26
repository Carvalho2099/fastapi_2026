from http import HTTPStatus
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from fastapi_zero.schemas import (
    Message,
    UserList,
    UserSchema,
    UserPublic,
    FilterPage,
)
from fastapi_zero.models import User
from fastapi_zero.database import get_session
from fastapi_zero.security import (
    get_password_hash,
    get_current_user,
)

router = APIRouter(prefix='/users', tags=['users'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: Session):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    db_user = User(
        email=user.email,
        username=user.username,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def read_users(
    session: Session,
    current_user: CurrentUser,
    filter_users: Annotated[FilterPage, Depends()],
):
    users = await session.scalars(
        select(User).offset(filter_users.offset).limit(filter_users.limit)
    )
    return {'users': users.all()}


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
):
    user_db = await session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    try:
        user_db.email = user.email
        user_db.username = user.username
        user_db.password = get_password_hash(user.password)

        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)

        return user_db
    except IntegrityError:
        raise HTTPException(
            detail='Username or Email already exists',
            status_code=HTTPStatus.CONFLICT,
        )


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
async def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    user_db = await session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )
    await session.delete(user_db)
    await session.commit()

    return {'message': 'User deleted'}

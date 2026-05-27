from http import HTTPStatus
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from fastapi_zero.schemas import (
    Token,
)
from fastapi_zero.models import User
from fastapi_zero.database import get_session
from fastapi_zero.security import (
    verify_password,
    create_access_token,
    get_current_user,
)
from sqlalchemy.ext.asyncio import AsyncSession as Session


router = APIRouter(prefix='/auth', tags=['auth'])
Session = Annotated[Session, Depends(get_session)]
Oauth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: Oauth2Form,
    session: Session,
):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/refresh_token', response_model=Token)
async def refresh_access_token(user: User = Depends(get_current_user)):
    new_access_token = create_access_token(data={'sub': user.email})

    return {'access_token': new_access_token, 'token_type': 'bearer'}

from pwdlib import PasswordHash
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jwt import encode
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession as Session
from fastapi import Depends, HTTPException
from jwt import decode, DecodeError, ExpiredSignatureError
from http import HTTPStatus
from sqlalchemy import select

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.settings import Settings

settings = Settings()
pdw_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})

    encode_jwt = encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encode_jwt


def get_password_hash(password: str):
    return pdw_context.hash(password)


def verify_password(plain_password: str, hashed_passord: str):
    return pdw_context.verify(plain_password, hashed_passord)


async def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject_email = payload.get('sub')
        if not subject_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception
    except ExpiredSignatureError:
        raise credentials_exception

    user = await session.scalar(
        select(User).where(User.email == subject_email)
    )
    if not user:
        raise credentials_exception

    return user

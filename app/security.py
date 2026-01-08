from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.settings import settings

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')

TokenDep = Annotated[str, Depends(oauth2_scheme)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    session: AsyncSessionDep,
    token: TokenDep,
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

        if not (subject_email := payload.get('sub')):
            raise credentials_exception

    except DecodeError as exc:
        raise credentials_exception from exc

    if not (
        user := await session.scalar(
            select(User).where(User.email == subject_email)
        )
    ):
        raise credentials_exception

    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    return encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, pwd_hash: str) -> bool:
    """Verify the password against the hash.

    Args:
        password (str): The plain password to verify.
        pwd_hash (str): The hash of the password.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    return pwd_context.verify(password, pwd_hash)

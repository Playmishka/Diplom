from datetime import datetime
from jwt import InvalidTokenError
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from starlette import status

from auth import utils
from models.modelsDB import user
from models.modelsData import UserSchema
from DB import get_session, Session
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Authentication"])
oAuth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


def validate_auth_user_login(
        username: str = Form(),
        password: str = Form(),
        session: Session = Depends(get_session)
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )
    if not (_user := session.query(user).filter(user.c.username == username).first()):
        raise unauthed_exc
    if utils.validate_password(
            password=password,
            hashed_password=utils.hash_password(_user.password)
            #TODO убрать при использовании хэшированных паролей в БД
    ):
        return _user

    raise unauthed_exc


@router.post("/login", response_model=TokenInfo)
def auth_user_issue_jwt(
        _user: UserSchema = Depends(validate_auth_user_login)
):
    jwt_payload = {
        "sub": _user.username,
    }
    access_token = utils.encode_jwt(jwt_payload)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


def get_current_token_payload(
        token: str = Depends(oAuth2_bearer)
):
    try:
        payload = utils.decode(
            token=token
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {e}",
        )
    return payload


def get_current_auth_user(
        payload: dict = Depends(get_current_token_payload),
        session: Session = Depends(get_session)
):
    username: str | None = payload.get("sub")
    if not (_user := session.query(user).filter(user.c.username == username).first()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid",
        )
    return _user


@router.get("users/me")
def auth_user_check_self_info(
        _user: UserSchema = Depends(get_current_auth_user),
        payload: dict = Depends(get_current_token_payload)
):
    return {
        "username": _user.username,
        "logged_in": payload.get("iat"),
    }

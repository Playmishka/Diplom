from datetime import datetime, timedelta

import jwt
from models.modelsData import Auth_JWT
import bcrypt

auth = Auth_JWT()


def encode_jwt(
        payload: dict,
        private_key: str = auth.private_key_path.read_text(),
        algorithm: str = auth.algorithm,
        expire_minutes: int = auth.access_token_exp_minutes,
        expire_timedelta: timedelta | None = None
) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()

    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)

    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm)
    return encoded


def decode(
        token: str | bytes,
        public_key: str = auth.public_key_path.read_text(),
        algorithm: str = auth.algorithm
) -> str:
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


# Хеширование пароля
def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


# Валидация пароля
def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)

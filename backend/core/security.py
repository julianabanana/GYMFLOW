"""
Utilidades de seguridad (core, según AGENTS.md): hash de contraseñas y JWT.

Estas son utilidades técnicas genéricas (RN-12, HU-10) — la lógica de negocio de
login/roles/expiración deslizante (RN-11) se implementa en `auth/` al construir
spec/features/003-autenticacion-segura, no aquí.
"""
from datetime import datetime, timedelta, timezone as dt_timezone

import jwt
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(data: dict, expires_minutes: int | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(dt_timezone.utc) + timedelta(
        minutes=expires_minutes or settings.jwt_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

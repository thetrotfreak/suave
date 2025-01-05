from datetime import datetime, timedelta, timezone

from fastapi.security import HTTPAuthorizationCredentials
from joserfc.jwt import encode, JWTClaimsRegistry

from .lifespan import Config


def oauth_user_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a new JWT Bearer token using `data` as payload
    """
    header = {"alg": "HS256"}

    if not Config.ALGORITHM == header.get("alg"):
        raise ValueError(f"Only 'ALGORITHM' {Config.ALGORITHM} is unsupported")
    if expires_delta is None:
        expires_delta = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    claims = data.copy()
    claims.update(
        {
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + expires_delta,
        }
    )

    key = Config.SECRET_KEY
    token = encode(header, claims, key)
    if Config.DEBUG:
        print(f"{token=}")
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

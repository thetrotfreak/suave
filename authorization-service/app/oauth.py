from datetime import datetime, timedelta, timezone

from fastapi.security import HTTPAuthorizationCredentials
from joserfc.jwt import encode, JWTClaimsRegistry

from .lifespan import Config

claims_requests = JWTClaimsRegistry()


def oauth_user_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a new JWT Bearer token using `data` as payload
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=30)

    header = {"alg": "HS256"}
    claims = data
    claims.update(
        {
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + expires_delta,
        }
    )

    if Config.env.get("ALGORITHM") == header.get("alg"):
        from joserfc.jwk import OctKey

        key = OctKey.import_key(Config.env.get("SECRET_KEY"))
        token = encode(header, claims, key)

        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

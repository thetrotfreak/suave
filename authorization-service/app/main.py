from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import (
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from joserfc import errors
from joserfc.jwk import OctKey
from joserfc.jwt import decode, JWTClaimsRegistry
from passlib.hash import scrypt
from passlib.utils import saslprep
from pydantic import ValidationError
from sqlmodel import select

from .dependency import Authorization, Database, DatabaseSession
from .lifespan import Config, lifespan
from .models import Token, User, UserBase, UserCreate, UserPublic
from .oauth import oauth_user_token

app = FastAPI(title="Suave Survey Authorization API", lifespan=lifespan)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/authorization-service/v1/sign-in")


@app.get("/")
@app.get("/api/authorization-service/v1")
@app.get("/api/authorization-service/v1/health")
async def root():
    return {"message": "ok"}


@app.post(
    "/api/authorization-service/v1/token",
    responses={status.HTTP_201_CREATED: {"model": HTTPAuthorizationCredentials}},
)
async def token(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        _token = decode(value=_token, key=Config.SECRET_KEY)
        if Config.DEBUG:
            print(f"{_token.claims=}")
        if Database.cache.get(_token.claims.get("sub")) is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        JWTClaimsRegistry().validate(_token.claims)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Token could not be validated\nPlease refresh the token",
        )
    else:
        # TODO: refresh the token
        # generate a new one
        # blacklist the old one
        new_token = oauth_user_token(dict.fromkeys(["sub"], _token.claims.get("sub")))
        Database.cache.set(
            _token.claims.get("sub"),
            new_token.credentials,
            ex=timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES).seconds,
        )
        return new_token


@app.post(
    "/api/authorization-service/v1/sign-up",
    description="Users are required to sign up for an account in the Suave Authorization Service",
    responses={
        status.HTTP_201_CREATED: {
            "model": UserPublic,
        }
    },
)
async def sign_up(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DatabaseSession,
):
    try:
        user = User.model_validate(
            form,
            update={"password_hash": scrypt.hash(secret=saslprep(form.password))},
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please check your username and/or password",
        )
    else:
        db.add(user)
        db.commit()
        db.refresh(user)
        return UserPublic(id=user.id, username=user.username)


@app.post(
    "/api/authorization-service/v1/sign-in",
    description="""
    Users are required to sign in using the OAuth flow and obtain a token.
    The token expires 30 minutes after issuance.
    The token is required for any further interaction with Suave Survey API.
    """,
    response_class=RedirectResponse,
    responses={
        status.HTTP_200_OK: {
            "model": Token,
        },
        status.HTTP_201_CREATED: {
            "model": UserPublic,
        },
        status.HTTP_307_TEMPORARY_REDIRECT: {},
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {},
    },
)
async def sign_in(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DatabaseSession,
):
    # find a user record
    try:
        UserBase.model_validate(UserBase(username=form.username))
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please check your email",
        )
    else:
        user = db.exec(select(User).where(User.username == form.username)).one_or_none()
        print(f"{user=}")
        if user is None:
            # return "api/authorization-service/v1/sign-up"
            return RedirectResponse(url="sign-up")
            # TODO: use redirect
            # raise HTTPException(
            #     status_code=status.HTTP_404_NOT_FOUND,
            #     detail="You do not exist in our system\nPlease sign up",
            # )

        # user was found in our system
        # match the user record against the form
        elif scrypt.verify(secret=form.password, hash=user.password_hash):
            # password hash verification passed

            # get the token associated with the user id
            if token := Database.cache.get(user.id.urn):
                return Token(access_token=token)

            # generate a new token if no token was associated with the verified user
            token = oauth_user_token(data={"sub": user.id.urn})

            # TODO: site responsible for token generation should also cache it
            # store the token as value against the user id
            Database.cache.set(
                user.id.urn,
                token.credentials,
                ex=timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES).seconds,
            )
            return Token(token_type=token.scheme, access_token=token.credentials)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )


@app.post(
    "/api/authorization-service/v1/sign-out",
    description="Users can sign out to destroy their session with Suave Survey.",
)
async def sign_out(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        _token = decode(
            value=token,
            key=Config.SECRET_KEY,
            # TODO: store ALGORITHM as List[str] in .env and parse as such, making it ALGORITHMS
            algorithms=[Config.ALGORITHM],
        )
        JWTClaimsRegistry().validate(_token.claims)
    except errors.BadSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except errors.ExpiredTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except errors.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    else:
        # TODO: should we set the 'exp' claim to 0
        Database.cache.delete(_token.claims.get("sub"))

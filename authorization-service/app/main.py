from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from joserfc import errors
from joserfc.jwt import decode
from passlib.hash import scrypt
from passlib.utils import saslprep
from sqlmodel import select

from .dependency import Authorization, Database, DatabaseSession
from .lifespan import Config, lifespan
from .models import Token, User, UserCreate
from .oauth import claims_requests, oauth_user_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/authorization-service/v1/token")
app = FastAPI(title="Suave Survey Authorization API", lifespan=lifespan)


@app.get("/")
@app.get("/api/authorization-service/v1")
@app.get("/api/authorization-service/v1/health")
async def index():
    return "OK"


@app.post("/api/authorization-service/v1/token", description="Not Implemented")
async def token():
    pass


@app.post(
    "/api/authorization-service/v1/sign-up",
    description="Users are required to sign up for an account in the Suave Authorization Service",
)
async def sign_up(
    request: UserCreate,
    db: DatabaseSession,
):
    user = User().model_validate(
        request,
        update={"password_hash": scrypt.hash(secret=saslprep(request.password))},
    )
    db.add(user)
    db.commit()
    return {}


@app.post(
    "/api/authorization-service/v1/sign-in",
    description="""
    Users are required to sign in using the OAuth flow and obtain a token.
    The token expires in 1800 seconds after issuance.
    The token is required for any further interaction with Suave Survey API.
    """,
)
async def sign_in(
    request: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DatabaseSession,
):
    # find a user record
    user = db.exec(select(User).where(User.username == request.username)).one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # match the user record against the request
    elif scrypt.verify(secret=request.password, hash=user.password_hash):

        # get the token associated with the user id
        if token := Database.store.get(user.id.urn):
            return Token(access_token=token)

        # generate a new token if no token was associated with the verified user
        token = oauth_user_token(data={"sub": user.id.urn})

        # store the token as value against the user id
        Database.store.set(user.id.urn, token.credentials)
        return Token(token_type=token.scheme, access_token=token.credentials)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post(
    "/api/authorization-service/v1/sign-out",
    description="Users can sign out to destroy their session with Suave Survey.",
)
async def sign_out(authorization: Authorization):
    try:
        token = decode(
            value=authorization.credentials,
            key=Config.env.get("SECRET_KEY"),
            algorithms=[Config.env.get("ALGORITHM")],
        )
        claims_requests.validate(token.claims)
    except errors.BadSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except errors.ExpiredTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    # TODO use more JWT errors
    else:
        # TODO use background task
        # blacklist the token in redis for a logged out user
        Database.store.set(token.claims.get("sub"), authorization.credentials)

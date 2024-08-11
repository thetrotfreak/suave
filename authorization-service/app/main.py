from fastapi import FastAPI
from joserfc import jwt

from .lifespan import lifespan_setup_database
from .models import SignInRequest

app = FastAPI(lifespan=lifespan_setup_database)


@app.get("/")
@app.get("/api/authorization-service/v1")
@app.get("/api/authorization-service/v1/health")
async def index():
    return "OK"


@app.get("/api/authorization-service/v1/token")
async def token():
    pass


@app.post("/api/authorization-service/v1/sign-up")
async def sign_up():
    pass


@app.post("/api/authorization-service/v1/sign-in")
async def sign_in(request: SignInRequest):
    pass


@app.post("/api/authorization-service/v1/sign-out")
async def sign_out():
    pass

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from src.database import init_db
from src.logger import logger
from src.user_service import UserService


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
user_service = UserService()


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await user_service.get_user_services(user_id)

    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user

import os
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.database import init_db
from src.logger import logger
from src.user_service import UserService


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Initializing database...")
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_service = UserService()


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await user_service.get_user_services(user_id)

    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user


@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    file_content = await file.read()
    print(f"Tamanho do arquivo recebido: {len(file_content)} bytes")

    await file.seek(0)

    save_path = f"audios/{file.filename}"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "message": "Áudio salvo com sucesso"}

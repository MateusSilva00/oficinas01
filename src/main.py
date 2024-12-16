import os
import shutil
import sqlite3
from contextlib import asynccontextmanager
from time import sleep

import adafruit_dht
import board
from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.assistant_openai import PersonalAssistant
from src.database import get_db_connection, init_db
from src.face_detection import face_detection, register_user_face
from src.logger import logger
from src.user_service import UserService

global UserPersonalAssistant


class UserRegistration(BaseModel):
    username: str
    services: list


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

    app.state.UserPersonalAssistant = PersonalAssistant(user["username"])

    return user


@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):

    await file.seek(0)

    save_path = f"audios/{file.filename}"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "message": "Áudio salvo com sucesso"}


@app.get("/play-zoey-response/")
async def play_zoey_response():
    if not hasattr(app.state, "UserPersonalAssistant"):
        raise HTTPException(
            status_code=400, detail="UserPersonalAssistant não foi inicializada"
        )

    message_to_zoey = app.state.UserPersonalAssistant.input_audio_to_text()
    app.state.UserPersonalAssistant.input_message(message_to_zoey)
    response = app.state.UserPersonalAssistant.get_response_message()
    logger.debug(f"Response: {response}")
    app.state.UserPersonalAssistant.get_output_audio(response)

    return {"Status": "OK", "Response": response}


@app.post("/register-face")
async def register_face(username: str = Body(..., media_type="text/plain")):
    logger.debug(f"Registering face for user: {username}")
    register_user_face(username)


@app.post("/register-user")
async def register_user(user_data: UserRegistration):
    services_mapping = {"B3": 0, "Bible": 0, "News": 0, "Soccer": 0}

    for service in user_data.services:
        if service in services_mapping:
            services_mapping[service] = 1

    conn = get_db_connection()

    with open("trained_data.yml", "r") as file:
        face_data = file.read()

    try:
        conn.execute(
            """
                    INSERT INTO users (username, b3, bible, news, soccer, yaml_face)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
            (
                user_data.username,
                services_mapping["B3"],
                services_mapping["Bible"],
                services_mapping["News"],
                services_mapping["Soccer"],
                face_data,
            ),
        )

        conn.commit()
        os.remove("trained_data.yml")

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")

    finally:
        conn.close()

    return {"Message": "Usuario cadastrado com sucesso!"}


@app.post("/face_detection")
def user_face_detection(username: str = Body(..., media_type="text/plain")):
    conn = get_db_connection()

    query = f"SELECT yaml_face, user_id FROM users WHERE username = '{username}'"

    face_data = conn.execute(query).fetchone()

    with open("trained_data.yml", "w") as file:
        file.write(face_data[0])

    _id = face_data[1]

    conn.close()
    face_detection(username)

    return {"Message": "Reconhecimento facial realizado com sucesso!", "User ID": _id}


@app.get("/temperature_humidity")
async def get_temperature_humidity():
    dht_device = adafruit_dht.DHT11(board.D4)

    temperature = dht_device.temperature
    humidity = dht_device.humidity

    while temperature is None or humidity is None:
        temperature = dht_device.temperature
        humidity = dht_device.humidity

        if temperature is not None and humidity is not None:
            return {"temperature": temperature, "humidity": humidity}

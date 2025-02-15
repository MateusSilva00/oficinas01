import os
import random
import time
import tkinter as tk
from tkinter import messagebox

import cv2
import numpy as np
from PIL import Image

from src.logger import logger


def face_detection(username: str):
    # recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trained_data.yml")
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
    font = cv2.FONT_HERSHEY_SIMPLEX

    names = ["", username]
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        logger.debug("Erro ao abrir a câmera para reconhecimento.")
        print("Erro ao abrir a câmera")
        return

    cam.set(3, 640)
    cam.set(4, 480)
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    user_recognized = False

    logger.debug(f"Iniciando reconhecimento facial para {username}")

    while True:
        ret, img = cam.read()
        img = cv2.flip(img, 1)
        if not ret:
            logger.debug("Falha ao capturar imagem durante reconhecimento.")
            print("Falha ao capturar imagem.")
            continue

        converted_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        faces = faceCascade.detectMultiScale(
            converted_image,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for x, y, w, h in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (128, 203, 196), 2)
            _id, accuracy = recognizer.predict(converted_image[y : y + h, x : x + w])

            if accuracy < 100:
                accuracy_value = round(100 - accuracy)
                logger.debug(
                    f"Usuário {username} reconhecido com acurácia de {accuracy_value}%"
                )
                if accuracy_value >= 60 and not user_recognized:
                    user_recognized = True
                    messagebox.showinfo(
                        "Reconhecimento", f"Usuário {username} reconhecido com sucesso!"
                    )
                    cam.release()
                    cv2.destroyAllWindows()
                    return
            else:
                accuracy_value = round(100 - accuracy)

            cv2.putText(
                img,
                f"{username} - {accuracy_value}%",
                (x + 5, y - 5),
                font,
                1,
                (244, 244, 244),
                1,
            )

        cv2.imshow("Reconhecimento Facial", img)
        k = cv2.waitKey(10) & 0xFF
        if k == 27:
            logger.debug("Reconhecimento facial encerrado pelo usuário.")
            break

    cam.release()
    cv2.destroyAllWindows()


def register_user_face(username):
    SAMPLE = 20
    font = cv2.FONT_HERSHEY_SIMPLEX

    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)

    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_alt.xml"
    )

    logger.debug(f"Iniciando cadastro do usuário: {username}")

    count = 0
    face_id = random.randint(1, 1000)  # Gerar um ID para o usuário uma vez

    cv2.namedWindow("Cadastrando usuário")

    while True:
        ret, img = cam.read()

        if not ret:
            logger.error("Falha na captura do vídeo.")
            break

        img = cv2.flip(img, 1)
        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(converted_image, 1.3, 5)

        cv2.putText(
            img, f"Amostras capturadas: {count}", (10, 20), font, 1, (244, 244, 244), 1
        )

        for x, y, w, h in faces:
            count += 1
            logger.debug(
                f"Total de amostras capturadas para {username}: {count}/{SAMPLE}"
            )

            cv2.imwrite(
                f"user_data/face_{username}_{face_id}_{count}.jpg",
                converted_image[y : y + h, x : x + w],
            )

            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

            if count >= SAMPLE:
                break

        cv2.imshow("Cadastrando usuário", img)

        time.sleep(0.5)

        if count >= SAMPLE:
            break

        # Pressionar 'q' para sair manualmente
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()  # Fechar todas as janelas

    logger.debug(
        f"Cadastro do usuário {username} concluído com {count} amostras capturadas."
    )

    # Mensagem de cadastro concluído
    messagebox.showinfo("Cadastro", f"Usuário {username} cadastrado com sucesso!")
    train_data()


# Função para treinar os dados
def train_data():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_alt.xml"
    )

    logger.debug("Iniciando treinamento dos dados.")

    def Images_And_Labels(path):
        imagesPaths = [os.path.join(path, f) for f in os.listdir(path)]
        faceSamples = []
        ids = []

        for imagePath in imagesPaths:
            gray_image = Image.open(imagePath).convert("L")
            img_arr = np.array(gray_image, "uint8")
            _id = int(os.path.split(imagePath)[-1].split("_")[-2])
            faces = detector.detectMultiScale(img_arr)

            for x, y, w, h in faces:
                faceSamples.append(img_arr[y : y + h, x : x + w])
                ids.append(_id)

        return faceSamples, ids

    def clean_folder(path):
        for file in os.listdir(path):
            os.remove(os.path.join(path, file))

    faces, ids = Images_And_Labels("user_data")
    recognizer.train(faces, np.array(ids))
    recognizer.write("trained_data.yml")
    clean_folder("user_data")

    logger.debug("Treinamento concluído e dados salvos.")


if __name__ == "__main__":
    # register_user_face("will")
    face_detection("will")

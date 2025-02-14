import random
import time
from tkinter import messagebox

import cv2

from src.logger import logger


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
    while True:
        ret, img = cam.read()

        if not ret:
            logger.error("Falha na captura do vídeo.")
            break

        img = cv2.flip(img, 1)
        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(converted_image, 1.3, 5)
        time.sleep(0.8)

        cv2.putText(
            img,
            f"Amostras capturadas: {count}",
            (10, 20),
            font,
            1,
            (244, 244, 244),
            1,
        )

        face_id = random.randint(1, 1000)

        for x, y, w, h in faces:
            count += 1
            logger.debug(
                f"Total de amostras capturadas para {username}: {count}/{SAMPLE}"
            )
            cv2.imwrite(
                f"user_data/face_{username}_{face_id}_{count}.jpg",
                converted_image[y : y + h, x : x + w],
            )
            if count >= SAMPLE:
                break

        cv2.imshow("Cadastrando usuário", img)

        if count >= SAMPLE:
            break

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()

    logger.debug(
        f"Cadastro do usuário {username} concluído com {count} amostras capturadas."
    )

    messagebox.showinfo("Cadastro", f"Usuário {username} cadastrado com sucesso!")

    # train_data()


register_user_face("will")

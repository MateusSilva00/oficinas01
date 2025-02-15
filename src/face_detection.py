import os
import random
import time
from tkinter import messagebox

import cv2
import numpy as np
from PIL import Image
from picamera2 import Picamera2
from picamera2 import Picamera2

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
        return False

    cam.set(3, 640)
    cam.set(4, 480)
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    user_recognized = False

    logger.debug(f"Iniciando reconhecimento facial para {username}")

    start_time = time.time()  # Registro do tempo inicial
    MAX_TIME = 35

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
                    return True
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

        elapsed_time = time.time() - start_time
        if elapsed_time > MAX_TIME:
            logger.debug(
                f"Tempo limite de {MAX_TIME} segundos atingido. Usuário não encontrado."
            )
            messagebox.showwarning(
                "Reconhecimento",
                f"Usuário {username} não encontrado em {MAX_TIME} segundos.",
            )
            cam.release()
            cv2.destroyAllWindows()
            return False

    cam.release()
    cv2.destroyAllWindows()
    return False


def register_user_face(username):
    SAMPLE = 10
    font = cv2.FONT_HERSHEY_SIMPLEX

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "XRGB8888"})
    picam2.configure(config)
    picam2.start()

    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt.xml")

    logger.debug(f"Iniciando cadastro do usuário: {username}")

    count = 0
    face_id = random.randint(1, 1000)
    window_name = "Cadastrando usuário"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Centralizar a janela na tela 1024x768
    screen_width = 1024
    screen_height = 768
    window_x = (screen_width - 640) // 2
    window_y = (screen_height - 480) // 2
    cv2.moveWindow(window_name, window_x, window_y)

    while count < SAMPLE:
        frame = picam2.capture_array()
        img = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # Remove canal alfa e ajusta cores

        img = cv2.flip(img, 1)  # Espelhamento horizontal

        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Para detecção de rosto
        faces = detector.detectMultiScale(converted_image, 1.3, 5)

        cv2.putText(img, f"Amostras capturadas: {count}", (10, 20), font, 1, (244, 244, 244), 1)

        for x, y, w, h in faces:
            count += 1
            logger.debug(f"Total de amostras capturadas para {username}: {count}/{SAMPLE}")

            cv2.imwrite(
                f"user_data/face_{username}_{face_id}_{count}.jpg",
                converted_image[y:y+h, x:x+w]
            )

            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

            if count >= SAMPLE:
                break

        cv2.imshow(window_name, img)
        time.sleep(0.5)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    picam2.stop()
    cv2.destroyAllWindows()

    logger.debug(f"Cadastro do usuário {username} concluído com {count} amostras capturadas.")
    messagebox.showinfo("Cadastro", f"Usuário {username} cadastrado com sucesso!")

    train_data()
    
    
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
    register_user_face("will")
    #face_detection("will")

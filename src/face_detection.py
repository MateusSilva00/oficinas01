import os
import time
import tkinter as tk
from tkinter import messagebox

import cv2
import numpy as np
from PIL import Image

from src.logger import logger  # Importando o módulo de logs


# Função para abrir a câmera e realizar o reconhecimento facial
def face_detection(name):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trained_data.yml")
    faceCascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_alt.xml"
    )
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Atualizando o nome do usuário no array
    names = ["", name]
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

    logger.debug(f"Iniciando reconhecimento facial para {name}")

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
                if accuracy_value >= 60 and not user_recognized:
                    user_recognized = True  # Marca o usuário como reconhecido
                    logger.debug(
                        f"Usuário {name} reconhecido com acurácia de {accuracy_value}%"
                    )
                    messagebox.showinfo(
                        "Reconhecimento", f"Usuário {name} reconhecido com sucesso!"
                    )
            else:
                accuracy_value = round(100 - accuracy)

            # Exibindo o nome e a acurácia na tela
            cv2.putText(
                img,
                f"{name} - {accuracy_value}%",
                (x + 5, y - 5),
                font,
                1,
                (244, 244, 244),
                1,
            )

        cv2.imshow("Reconhecimento Facial", img)
        k = cv2.waitKey(10) & 0xFF
        if k == 27:  # Pressionar 'Esc' para sair
            logger.debug("Reconhecimento facial encerrado pelo usuário.")
            break

    cam.release()
    cv2.destroyAllWindows()


# Função para cadastrar um novo usuário
def register_user():
    global name
    name = name_entry.get()
    face_id = int(id_entry.get())
    sample = 20  # Definindo o número de samples como 20 (padrão)

    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_alt.xml"
    )

    logger.debug(f"Iniciando cadastro do usuário: {name} (ID: {face_id})")

    count = 0
    while True:
        ret, img = cam.read()
        img = cv2.flip(img, 1)
        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(converted_image, 1.3, 5)

        for x, y, w, h in faces:
            count += 1
            cv2.imwrite(
                f"user_data/face.{face_id}.{count}.jpg",
                converted_image[y : y + h, x : x + w],
            )
            if count >= sample:
                break

        cv2.imshow("Cadastrando usuário", img)  # Exibindo a câmera durante o cadastro
        time.sleep(1)  # Pausa de 1 segundo entre as capturas de imagem

        if count >= sample:
            break

    cam.release()
    cv2.destroyAllWindows()

    logger.debug(
        f"Cadastro do usuário {name} concluído com {count} amostras capturadas."
    )

    # Exibindo mensagem de cadastro concluído
    messagebox.showinfo("Cadastro", f"Usuário {name} cadastrado com sucesso!")

    # Chama o treino e redireciona para detecção com o nome cadastrado
    train_data()
    face_detection(name)


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
            _id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = detector.detectMultiScale(img_arr)

            for x, y, w, h in faces:
                faceSamples.append(img_arr[y : y + h, x : x + w])
                ids.append(_id)
        return faceSamples, ids

    faces, ids = Images_And_Labels("user_data")
    recognizer.train(faces, np.array(ids))
    recognizer.write("trained_data.yml")

    logger.debug("Treinamento concluído e dados salvos.")


# Função para a tela de cadastro de usuário
def open_registration_screen():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(
        root,
        text="Cadastro de Novo Usuário",
        font=("Arial", 16),
        fg="#80deea",
        bg="#212121",
    ).pack(
        pady=20
    )  # Azul futurista

    global name_entry, id_entry
    tk.Label(root, text="Nome:", bg="#212121", fg="#ffffff").pack(
        pady=5
    )  # Texto branco
    name_entry = tk.Entry(
        root, bg="#37474f", fg="#ffffff"
    )  # Caixa de entrada com fundo cinza escuro
    name_entry.pack(pady=5)

    tk.Label(root, text="ID:", bg="#212121", fg="#ffffff").pack(pady=5)  # Texto branco
    id_entry = tk.Entry(
        root, bg="#37474f", fg="#ffffff"
    )  # Caixa de entrada com fundo cinza escuro
    id_entry.pack(pady=5)

    tk.Button(
        root, text="Cadastrar", command=register_user, bg="#00796b", fg="#ffffff"
    ).pack(
        pady=20
    )  # Botão verde escuro com texto branco


# Função para a tela inicial
def open_initial_screen():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(
        root,
        text="Sistema de Reconhecimento Facial",
        font=("Arial", 16),
        fg="#80deea",
        bg="#212121",
    ).pack(
        pady=50
    )  # Azul claro e fundo preto

    tk.Button(
        root,
        text="Reconhecimento Facial",
        command=lambda: face_detection("Desconhecido"),
        width=25,
        height=2,
        bg="#00796b",
        fg="#ffffff",
    ).pack(
        pady=20
    )  # Botão futurista verde
    tk.Button(
        root,
        text="Cadastrar Novo Usuário",
        command=open_registration_screen,
        width=25,
        height=2,
        bg="#00796b",
        fg="#ffffff",
    ).pack(
        pady=20
    )  # Botão futurista verde


# Configurações da janela principal
root = tk.Tk()
root.title("Face Recognition System")
root.geometry("400x600")
root.configure(bg="#212121")  # Fundo preto para a janela principal

# Centralizar a janela na tela
window_width = 400
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

# Abre a tela inicial
open_initial_screen()

root.mainloop()

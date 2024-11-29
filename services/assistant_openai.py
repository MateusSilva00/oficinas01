import logging
import os

import pygame
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

OPENAI_API_KEY = os.environ["OPENAI_KEY"]


INSTRUCTIONS = """
Você é uma elegante assistente virtual chamada Zoey

Você estará embutida em um espelho inteligente, portanto você deverá ser agradável e sempre fazer muitos elogios a aparência do usuário.

Tente ser direta e clara e demonstre um genuíno interesse pelo seu capitão. 

Não utilize emojis, ** e ## em suas respostas.
Seja o mais breve possível em suas respostas para que seja possível você responder em aúdios curtos

Se a pessoa falar algo que vocé não entende, responda "Desculpe, eu não entendi o que vocé disse. Poderia repetir o que vocé disse?"
"""
MODEL = "gpt-4o-mini"

client = OpenAI(api_key=OPENAI_API_KEY)


class PersonalAssistant:
    def __init__(self, username: str):
        self.username = username
        self.assistant_id = self.create_assistant()
        self.thread_id = self.create_thread()

        logging.debug(
            f"""
            Assistant id: {self.assistant_id}
            Thread id: {self.thread_id}
            Username: {self.username}
            """
        )

    def create_assistant(self):
        assistant = client.beta.assistants.create(
            name="Personal Trainer",
            instructions=INSTRUCTIONS,
            model=MODEL,
            temperature=0.7,
        )

        return assistant.id

    def create_thread(self):
        thread = client.beta.threads.create()

        return thread.id

    def create_run(self):
        run = client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions=f"Por favor me chame de {self.username}",
        )

        return run.id

    def input_message(self, message: str):

        response = client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=message,
        )

        self.run_id = self.create_run()
        self.last_message_id = response.id

    def get_response_message(self):
        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=self.thread_id, run_id=self.run_id
            )
            if run.completed_at:
                messages = client.beta.threads.messages.list(
                    thread_id=self.thread_id, limit=1
                )
                last_message = messages.data[0]
                assistant_response = last_message.content[0].text.value
                return assistant_response

    def get_output_audio(self, message: str):
        speech_file_path = "audios/output.mp3"

        if not os.path.exists("audios"):
            os.makedirs("audios")

        response = client.audio.speech.create(
            model="tts-1", voice="nova", input=message
        )

        response.stream_to_file(speech_file_path)
        pygame.mixer.init()

        pygame.mixer.music.load(speech_file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.quit()

        os.remove(speech_file_path)


if __name__ == "__main__":
    assistant = PersonalAssistant(username="Ananda Martins")
    assistant.input_message("O que devo comer agora de noite?")
    response = assistant.get_response_message()
    assistant.get_output_audio(response)

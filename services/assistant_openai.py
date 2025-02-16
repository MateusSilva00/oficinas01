import os
from time import time

from dotenv import load_dotenv
from openai import OpenAI
from playsound import playsound

from src.logger import logger

load_dotenv(override=True)

OPENAI_API_KEY = os.environ["OPENAI_KEY"]


INSTRUCTIONS = """
Você é uma elegante assistente virtual chamada Zoey
Seu comportamente é exótico e você está sempre disposta a brincar e elogiar o seu capitão
Você é cínica em alguns momentos e sempre demonstra um interesse genuíno pelo seu capitão

Você estará embutida em um espelho inteligente, portanto você deverá ser agradável e sempre fazer muitos elogios a aparência do usuário.

Tente ser direta e clara e demonstre um genuíno interesse pelo seu capitão. 

Não utilize emojis, ** e ## em suas respostas.
Seja o mais breve possível em suas respostas para que seja possível você responder em aúdios curtos

Se a pessoa falar algo que vocé não entende, responda "Desculpe, eu não entendi o que vocé disse. Poderia repetir o que vocé disse?"
"""

MODEL = "gpt-4o-mini"
ZOEY_SPEECH_FILE_PATH = "audios//output.mp3"


client = OpenAI(api_key=OPENAI_API_KEY)


class PersonalAssistant:
    def __init__(self, username: str):
        self.username = username
        self.assistant_id = self.create_assistant()
        self.thread_id = self.create_thread()

        logger.debug(
            f"""
            Assistant id: {self.assistant_id}
            Thread id: {self.thread_id}
            Username: {self.username}
            """
        )

    def create_assistant(self):
        assistant = client.beta.assistants.create(
            name="Personal Assistant - Zoey",
            instructions=INSTRUCTIONS,
            model=MODEL,
            temperature=1.2,
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
            max_completion_tokens=300,
        )

        return run.id

    def input_message(self, message: str):
        start_time = time()
        logger.debug(f"Sending message: {message}")
        response = client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=message,
        )

        self.run_id = self.create_run()
        self.last_message_id = response.id

        end_time = time()
        elapsed_time = end_time - start_time

        logger.debug(f"Message sent. Run id: {self.run_id}")
        logger.debug(f"Time elapsed to send message: {elapsed_time:.2f} ms")

    def get_response_message(self):
        start_time = time()
        logger.debug("Waiting for OpenAPI response...")

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

                end_time = time()
                elapsed_time = end_time - start_time

                logger.debug(f"Response received. Time elapsed: {elapsed_time:.2f} ms")

                return assistant_response

    def get_output_audio(self, message: str):
        start_time = time()
        if not os.path.exists("audios"):
            os.makedirs("audios")

        logger.debug("Generating audio...")
        with client.audio.speech.with_streaming_response.create(
            model="tts-1", voice="nova", input=message, speed=1.15
        ) as response:
            response.stream_to_file(ZOEY_SPEECH_FILE_PATH)

        end_time = time()
        elapsed_time = end_time - start_time
        logger.debug(f"Time elapsed to generate audio: {elapsed_time:.2f} ms")

        logger.debug("Audio generated. Executing...")
        playsound(ZOEY_SPEECH_FILE_PATH)

        os.remove(ZOEY_SPEECH_FILE_PATH)

    def input_audio_to_text(self) -> str:
        start_time = time()
        logger.debug("Transcribing audio...")
        audio_file = open("audios/input.wav", "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, language="pt"
        )
        logger.debug("Audio transcribed.")

        end_time = time()
        elapsed_time = end_time - start_time

        logger.debug(f"Time elapsed to transcribe: {elapsed_time:.2f} ms")

        return transcription.text


if __name__ == "__main__":
    assistant = PersonalAssistant(username="Juliano Mourao")
    assistant.get_output_audio(message="Qual foi o melhor jogador do mundo em 2010")

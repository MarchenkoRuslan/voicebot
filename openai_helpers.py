import os
import openai
from config import settings

class OpenAIHandler:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.assistant = None
        self.thread = None
    
    async def transcribe_audio(self, audio_path: str) -> str:
        """Преобразование аудио в текст с помощью Whisper API"""
        with open(audio_path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ru"
            )
        return transcript.text

    async def get_assistant_response(self, user_message: str) -> str:
        """Получение ответа от Assistant API"""
        if not self.assistant:
            self.assistant = await self.client.beta.assistants.create(
                name="Voice Assistant",
                instructions="Ты - голосовой помощник. Отвечай кратко и информативно.",
                model="gpt-4-turbo-preview"
            )
        
        if not self.thread:
            self.thread = await self.client.beta.threads.create()

        # Добавляем сообщение пользователя в тред
        await self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_message
        )

        # Запускаем выполнение
        run = await self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )

        # Ждем завершения
        while True:
            run = await self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
            if run.status == 'completed':
                break

        # Получаем ответ
        messages = await self.client.beta.threads.messages.list(
            thread_id=self.thread.id
        )
        return messages.data[0].content[0].text.value

    async def text_to_speech(self, text: str, output_path: str) -> str:
        """Преобразование текста в речь"""
        response = await self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        response.stream_to_file(output_path)
        return output_path 
import os
import logging
import asyncio
from openai import AsyncOpenAI
import uuid
from src.services.user_service import UserService
from typing import Tuple, Optional, Dict, Any
from src.core.config import settings

class OpenAIService:
    def __init__(self, client, user_service: UserService):
        self.client = client
        self.user_service = user_service
        self.assistant_id = settings.ASSISTANT_ID

    async def transcribe_audio(self, file_path: str) -> str:
        """Transcribe audio file to text"""
        with open(file_path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
            return transcript.text

    async def validate_value(self, value: str) -> bool:
        """Validate the extracted value"""
        # Здесь можно добавить дополнительную валидацию
        return bool(value and len(value) > 2)

    async def create_and_poll_run(self, thread_id: str) -> Tuple[str, bool]:
        """Create run and poll for completion"""
        run = await self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        )

        max_retries = 60  # Максимальное время ожидания - 5 минут
        retry_count = 0
        
        while retry_count < max_retries:
            run_status = await self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            
            if run_status.status == 'completed':
                messages = await self.client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                response = messages.data[0].content[0].text.value
                # Проверяем, была ли вызвана функция
                was_function_called = bool(run_status.required_action and 
                    run_status.required_action.tool_calls)
                return response, was_function_called
                
            elif run_status.status in ['failed', 'cancelled', 'expired']:
                raise Exception(f"Run failed with status: {run_status.status}")
            
            retry_count += 1
            await asyncio.sleep(5)  # Увеличиваем интервал до 5 секунд
        
        raise Exception("Timeout waiting for assistant response")

    async def get_assistant_response(self, message: str, telegram_id: int) -> str:
        """Get response using Assistant API"""
        try:
            user = await self.user_service.get_user(telegram_id)
            
            if not user or not user.assistant_thread_id:
                thread = await self.client.beta.threads.create()
                if not user:
                    user = await self.user_service.create_user(telegram_id, thread.id)
                else:
                    user = await self.user_service.update_user_thread(user, thread.id)

            await self.client.beta.threads.messages.create(
                thread_id=user.assistant_thread_id,
                role="user",
                content=message
            )

            response, was_function_called = await self.create_and_poll_run(
                user.assistant_thread_id
            )

            if was_function_called and "SAVE_VALUE:" in response:
                value = response.split("SAVE_VALUE:")[1].strip()
                if await self.validate_value(value):
                    await self.user_service.update_user_values(user, value)
                    return f"Я определил вашу ключевую ценность: {value}"
                return "Извините, мне нужно больше информации для определения вашей ценности."

            return response

        except Exception as e:
            logging.error(f"Error in get_assistant_response: {e}")
            raise

    async def text_to_speech(self, text: str) -> str:
        """Convert text to speech"""
        response = await self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        output_path = f"audio_responses/{hash(text)}.mp3"
        response.stream_to_file(output_path)
        return output_path 
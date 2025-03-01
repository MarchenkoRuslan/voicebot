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
        logging.info(f"Created run {run.id} for thread {thread_id}")

        max_retries = 24  # Максимальное время ожидания - 2 минуты
        retry_count = 0
        
        while retry_count < max_retries:
            run_status = await self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            logging.info(f"Run status: {run_status.status}")
            
            if run_status.status == 'completed':
                messages = await self.client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                response = messages.data[0].content[0].text.value
                logging.info(f"Got response: {response}")
                return response, True
                
            elif run_status.status == 'requires_action':
                # Получаем требуемое действие
                required_actions = run_status.required_action.submit_tool_outputs.tool_calls
                logging.info(f"Required actions: {required_actions}")
                
                # Подтверждаем выполнение функции для каждого действия
                tool_outputs = []
                for action in required_actions:
                    tool_outputs.append({
                        "tool_call_id": action.id,
                        "output": "true"
                    })
                
                await self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                logging.info(f"Submitted tool outputs: {tool_outputs}")
                
            elif run_status.status in ['failed', 'cancelled', 'expired']:
                error_msg = f"Run failed with status: {run_status.status}"
                logging.error(error_msg)
                raise Exception(error_msg)
            
            retry_count += 1
            await asyncio.sleep(5)
        
        error_msg = f"Timeout waiting for assistant response after {max_retries * 5} seconds"
        logging.error(error_msg)
        raise Exception(error_msg)

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
            
            # Получаем список активных runs
            runs = await self.client.beta.threads.runs.list(
                thread_id=user.assistant_thread_id
            )
            
            # Отменяем все активные runs
            for run in runs.data:
                if run.status not in ['completed', 'failed', 'cancelled', 'expired']:
                    try:
                        await self.client.beta.threads.runs.cancel(
                            thread_id=user.assistant_thread_id,
                            run_id=run.id
                        )
                    except Exception as e:
                        logging.warning(f"Failed to cancel run {run.id}: {e}")
                    await asyncio.sleep(1)  # Даем время на отмену

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
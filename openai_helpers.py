import os
import json
from typing import Dict, Any
from openai import AsyncOpenAI
from config import settings
from database import async_session
from models import User
from sqlalchemy import select, insert
import uuid
import logging
from datetime import datetime
import sqlalchemy as sa

class OpenAIHandler:

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.assistant_id = os.getenv('ASSISTANT_ID')
    
    async def transcribe_audio(self, file_path: str) -> str:
        """Convert voice to text using Whisper API"""
        try:
            with open(file_path, 'rb') as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            logging.error(f"Error in transcribe_audio: {e}")
            raise

    async def validate_value(self, value: str) -> bool:
        """Валидация значения через Completions API"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{
                    "role": "system",
                    "content": "Ты - валидатор личностных ценностей. Твоя задача - проверить, является ли предоставленное значение осмысленной личностной ценностью."
                }, {
                    "role": "user",
                    "content": f"Является ли '{value}' осмысленной личностной ценностью? Ответь только True или False."
                }],
                functions=[{
                    "name": "validate_value",
                    "description": "Validates if the given value is a meaningful personal value",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "is_valid": {
                                "type": "boolean",
                                "description": "True if the value is valid, False otherwise"
                            }
                        },
                        "required": ["is_valid"]
                    }
                }],
                function_call={"name": "validate_value"}
            )
            
            result = response.choices[0].message.function_call.arguments
            return "true" in result.lower()
        except Exception as e:
            logging.error(f"Error in validate_value: {e}")
            return False

    async def save_user_value(self, telegram_id: int, value: str) -> bool:
        """Save validated user value to database"""
        if not await self.validate_value(value):
            return False

        async with async_session() as session:
            # Check if user exists
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user is None:
                # Create new user
                user = User(telegram_id=telegram_id, values=value)
                session.add(user)
            else:
                # Update existing user's values
                user.values = value

            await session.commit()
            return True

    async def get_assistant_response(self, message: str, telegram_id: int) -> str:
        """Get response using Assistant API"""
        try:
            async with async_session() as session:
                stmt = select(User).where(User.telegram_id == telegram_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if not user or not user.assistant_thread_id:
                    thread = await self.client.beta.threads.create()
                    if not user:
                        # Создаем SQL запрос с явным указанием всех полей
                        stmt = sa.text("""
                            INSERT INTO users (telegram_id, assistant_thread_id, values, created_at, updated_at)
                            VALUES (:telegram_id, :thread_id, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            RETURNING *
                        """)
                        result = await session.execute(
                            stmt,
                            {"telegram_id": telegram_id, "thread_id": thread.id}
                        )
                        user = result.mappings().one()
                    else:
                        user.assistant_thread_id = thread.id
                        await session.commit()
                        await session.refresh(user)

                # Отправляем сообщение ассистенту
                await self.client.beta.threads.messages.create(
                    thread_id=user.assistant_thread_id,
                    role="user",
                    content=message
                )

                # Запускаем ассистента
                run = await self.client.beta.threads.runs.create(
                    thread_id=user.assistant_thread_id,
                    assistant_id=self.assistant_id
                )

                # Ждем завершения
                while True:
                    run_status = await self.client.beta.threads.runs.retrieve(
                        thread_id=user.assistant_thread_id,
                        run_id=run.id
                    )
                    if run_status.status == 'completed':
                        break
                    elif run_status.status == 'failed':
                        raise Exception("Assistant run failed")

                # Получаем ответ
                messages = await self.client.beta.threads.messages.list(
                    thread_id=user.assistant_thread_id
                )
                response = messages.data[0].content[0].text.value

                # Если ассистент определил ценность, валидируем и сохраняем
                if "SAVE_VALUE:" in response:
                    value = response.split("SAVE_VALUE:")[1].strip()
                    if await self.validate_value(value):
                        user.values = value
                        await session.commit()
                        return f"Я определил вашу ключевую ценность: {value}"
                    else:
                        return "Извините, мне нужно больше информации, чтобы определить вашу ценность. Расскажите подробнее о себе."

                return response

        except Exception as e:
            logging.error(f"Error in get_assistant_response: {e}")
            raise

    async def text_to_speech(self, text: str) -> str:
        """Convert text to speech using TTS API"""
        output_path = f"audio_responses/response_{uuid.uuid4()}.mp3"
        try:
            response = await self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            await response.astream_to_file(output_path)
            return output_path
        except Exception as e:
            logging.error(f"Error in text_to_speech: {e}")
            raise 
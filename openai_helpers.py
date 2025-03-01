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
        """Validate the identified value using Completions API"""
        functions = [
            {
                "name": "validate_personal_value",
                "description": "Validates if the provided text represents a genuine personal value",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "is_valid": {
                            "type": "boolean",
                            "description": "True if the text represents a genuine personal value, False otherwise"
                        }
                    },
                    "required": ["is_valid"]
                }
            }
        ]

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a validator of personal values. Analyze the provided text and determine if it represents a genuine personal value. Return false for empty, nonsensical, or inappropriate responses."
                },
                {
                    "role": "user",
                    "content": f"Validate this personal value: {value}"
                }
            ],
            functions=functions,
            function_call={"name": "validate_personal_value"}
        )

        result = json.loads(response.choices[0].message.function_call.arguments)
        return result["is_valid"]

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
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()
                
                if not user or not user.assistant_thread_id:
                    thread = await self.client.beta.threads.create()
                    if not user:
                        # Явно указываем все поля, включая created_at
                        result = await session.execute(
                            insert(User).values({
                                'telegram_id': telegram_id,
                                'assistant_thread_id': thread.id,
                                'created_at': sa.text('CURRENT_TIMESTAMP'),
                                'updated_at': sa.text('CURRENT_TIMESTAMP'),
                                'values': None
                            }).returning(User)
                        )
                        user = result.scalar_one()
                    else:
                        user.assistant_thread_id = thread.id
                    await session.commit()
                thread_id = user.assistant_thread_id

            # Add message to thread
            await self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )

            # Run the assistant
            run = await self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )

            # Wait for completion
            while True:
                run_status = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                if run_status.status == 'completed':
                    break
                elif run_status.status == 'failed':
                    raise Exception("Assistant run failed")

            # Get the latest message
            messages = await self.client.beta.threads.messages.list(thread_id=thread_id)
            return messages.data[0].content[0].text.value

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
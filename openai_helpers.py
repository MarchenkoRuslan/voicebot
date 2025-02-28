import os
import json
from typing import Dict, Any
from openai import AsyncOpenAI
from config import settings
from database import async_session
from models import User
from sqlalchemy import select

class OpenAIHandler:

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
        )
        self.thread = None
    
    async def transcribe_audio(self, audio_path: str) -> str:
        """Convert audio to text using Whisper API"""
        with open(audio_path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
        return transcript.text

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

    async def get_assistant_response(self, user_message: str, telegram_id: int) -> str:
        """Get response from Assistant API with value identification"""
        if not self.thread:
            self.thread = await self.client.beta.threads.create()

        # Add user message to thread
        await self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_message
        )

        # Create and wait for run completion using create_and_poll
        run = await self.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=settings.ASSISTANT_ID,
            tools=[{
                "type": "function",
                "function": {
                    "name": "save_value",
                    "description": "Save an identified personal value to the database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "value": {
                                "type": "string",
                                "description": "The identified personal value"
                            }
                        },
                        "required": ["value"]
                    }
                }
            }]
        )

        # Get response
        messages = await self.client.beta.threads.messages.list(
            thread_id=self.thread.id
        )
        
        # Check if there was a function call
        tool_calls = run.required_action.submit_tool_outputs if run.required_action else None
        if tool_calls:
            for tool_call in tool_calls.tool_calls:
                if tool_call.function.name == "save_value":
                    args = json.loads(tool_call.function.arguments)
                    value = args["value"]
                    if await self.save_user_value(telegram_id, value):
                        return f"I've identified and saved your personal value: {value}"
                    else:
                        return "I couldn't validate the identified value. Could you please elaborate more on your values?"

        return messages.data[0].content[0].text.value

    async def text_to_speech(self, text: str, output_path: str) -> str:
        """Convert text to speech"""
        response = await self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        response.stream_to_file(output_path)
        return output_path 
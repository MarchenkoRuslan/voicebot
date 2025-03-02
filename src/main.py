import asyncio
import logging
import os
import sys
from pathlib import Path
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
from core.config import settings
from services.openai_service import OpenAIService
from core.database import async_session
from services.user_service import UserService
from openai import AsyncOpenAI

# Logging setup
logging.basicConfig(level=logging.INFO)

# Create necessary directories
os.makedirs("voice_messages", exist_ok=True)
os.makedirs("audio_responses", exist_ok=True)

# Initialize bot and dispatcher
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def get_openai_service():
    async with async_session() as session:
        user_service = UserService(session)
        return OpenAIService(client, user_service)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Hi! I'm a voice AI bot that can help identify your personal values. "
        "You can send me voice messages or text, and I'll analyze them to help "
        "understand your core values."
    )

@dp.message(F.voice)
async def handle_voice(message: types.Message):
    try:
        async with async_session() as session:
            user_service = UserService(session)
            openai_service = OpenAIService(client, user_service)
            
            # Download voice message
            voice = await bot.get_file(message.voice.file_id)
            file_path = f"voice_messages/{voice.file_id}.ogg"
            await bot.download_file(voice.file_path, file_path)
            
            await message.answer("Processing your message...")
            
            # Get text from voice message
            text = await openai_service.transcribe_audio(file_path)
            await message.answer(f"I heard: {text}")
            
            # Get response from assistant
            await message.answer("Analyzing your values...")
            response = await openai_service.get_assistant_response(text, message.from_user.id)
            
            # Convert response to voice
            await message.answer("Converting response to voice...")
            audio_response_path = await openai_service.text_to_speech(response)
            
            # Send voice and text response
            await message.answer(response)
            await message.answer_voice(voice=FSInputFile(audio_response_path))
            
    except Exception as e:
        logging.error(f"Error processing voice message: {e}")
        await message.answer("Sorry, there was an error processing your voice message.")
    finally:
        # Remove temporary files
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        if 'audio_response_path' in locals() and os.path.exists(audio_response_path):
            os.remove(audio_response_path)

@dp.message(lambda message: message.text and not message.text.startswith('/'))
async def handle_text(message: types.Message):
    try:
        async with async_session() as session:
            user_service = UserService(session)
            openai_service = OpenAIService(client, user_service)
            response = await openai_service.get_assistant_response(message.text, message.from_user.id)
            await message.answer(response)
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await message.answer("Sorry, there was an error processing your message.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 
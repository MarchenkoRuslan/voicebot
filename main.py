import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from config import settings
from openai_helpers import OpenAIHandler
from database import engine
from sqlalchemy import text
from aiogram.types import FSInputFile

# Logging setup
logging.basicConfig(level=logging.INFO)

# Create necessary directories
os.makedirs("voice_messages", exist_ok=True)
os.makedirs("audio_responses", exist_ok=True)

# Initialize bot and dispatcher
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Initialize OpenAI handler
openai_handler = OpenAIHandler()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Hi! I'm a voice AI bot. Send me a voice message, "
        "and I'll respond with voice!"
    )

@dp.message(F.voice)
async def handle_voice(message: types.Message):
    file_path = None
    audio_response_path = None
    try:
        # Download voice message
        voice = await bot.get_file(message.voice.file_id)
        file_path = f"voice_messages/{voice.file_id}.ogg"
        await bot.download_file(voice.file_path, file_path)
        
        await message.answer("Processing your message...")
        
        # Get text from voice message
        text = await openai_handler.transcribe_audio(file_path)
        await message.answer(f"I heard: {text}")
        
        # Get response from assistant
        await message.answer("Thinking about response...")
        response = await openai_handler.get_assistant_response(text, message.from_user.id)
        
        # Convert response to voice
        await message.answer("Converting response to voice...")
        audio_response_path = await openai_handler.text_to_speech(response)
        
        # Send voice and text response
        await message.answer(response)
        await message.answer_voice(voice=FSInputFile(audio_response_path))
        
    except Exception as e:
        logging.error(f"Error processing voice message: {e}")
        await message.answer("An error occurred while processing your voice message.")
    finally:
        # Remove temporary files
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if audio_response_path and os.path.exists(audio_response_path):
            os.remove(audio_response_path)

@dp.message(lambda message: message.text and not message.text.startswith('/'))
async def handle_text(message: types.Message):
    try:
        # Send processing message
        processing_msg = await message.answer("Processing your message...")

        # Get response from Assistant API
        response = await openai_handler.get_assistant_response(
            message.text,
            message.from_user.id
        )
        await message.answer(response)

        # Delete processing message
        await processing_msg.delete()

    except Exception as e:
        logging.error(f"Error processing text message: {e}")
        await message.answer("An error occurred while processing your message.")

async def test_db():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")

async def main():
    # First test database connection
    await test_db()
    # Then start the bot
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 
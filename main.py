import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import settings
from openai_helpers import OpenAIHandler
from database import engine
from sqlalchemy import text

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

@dp.message(lambda message: message.voice)
async def handle_voice(message: types.Message):
    file_path = None
    try:
        # Скачиваем голосовое сообщение
        voice = await bot.get_file(message.voice.file_id)
        file_path = f"voice_messages/{voice.file_id}.ogg"
        await bot.download_file(voice.file_path, file_path)
        
        await message.answer("Processing your message...")
        
        # Получаем текст из голосового сообщения и ответ от OpenAI
        text = await openai_handler.transcribe_audio(file_path)
        response = await openai_handler.get_assistant_response(text, message.from_user.id)
        
        await message.answer(response)
        
    except Exception as e:
        logging.error(f"Error processing voice message: {e}")
        await message.answer("An error occurred while processing your voice message.")
    finally:
        # Удаляем временный файл
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Temporary file {file_path} removed")

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
    # Сначала проверяем подключение к БД
    await test_db()
    # Затем запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 
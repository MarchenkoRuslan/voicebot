import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import settings
from openai_helpers import OpenAIHandler

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем необходимые директории
os.makedirs("voice_messages", exist_ok=True)
os.makedirs("audio_responses", exist_ok=True)

# Инициализация бота и диспетчера
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Инициализация OpenAI handler
openai_handler = OpenAIHandler()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я голосовой AI-бот. Отправь мне голосовое сообщение, "
        "и я отвечу тебе голосом!"
    )

@dp.message(lambda message: message.voice)
async def handle_voice(message: types.Message):
    try:
        # Отправляем сообщение о начале обработки
        processing_msg = await message.answer("Обрабатываю ваше сообщение...")

        # Скачивание голосового сообщения
        voice = await bot.get_file(message.voice.file_id)
        voice_path = f"voice_messages/{message.voice.file_id}.ogg"
        await bot.download_file(voice.file_path, voice_path)
        
        # Преобразование голоса в текст
        user_text = await openai_handler.transcribe_audio(voice_path)
        await message.answer(f"Ваш запрос: {user_text}")
        
        # Получение ответа от Assistant API
        assistant_response = await openai_handler.get_assistant_response(user_text)
        await message.answer(f"Ответ: {assistant_response}")
        
        # Преобразование ответа в голос
        response_audio_path = f"audio_responses/{message.voice.file_id}_response.mp3"
        await openai_handler.text_to_speech(assistant_response, response_audio_path)
        
        # Отправка голосового ответа
        await message.answer_voice(voice=types.FSInputFile(response_audio_path))
        
        # Удаление временных файлов
        os.remove(voice_path)
        os.remove(response_audio_path)
        
        # Удаляем сообщение о обработке
        await processing_msg.delete()
        
    except Exception as e:
        logging.error(f"Ошибка при обработке голосового сообщения: {e}")
        await message.answer("Произошла ошибка при обработке голосового сообщения.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 
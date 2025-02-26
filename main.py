import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import settings
from openai_helpers import OpenAIHandler

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
    try:
        # Send processing message
        processing_msg = await message.answer("Processing your message...")

        # Download voice message
        voice = await bot.get_file(message.voice.file_id)
        voice_path = f"voice_messages/{message.voice.file_id}.ogg"
        await bot.download_file(voice.file_path, voice_path)
        
        # Convert voice to text
        user_text = await openai_handler.transcribe_audio(voice_path)
        await message.answer(f"Your request: {user_text}")
        
        # Get response from Assistant API
        assistant_response = await openai_handler.get_assistant_response(user_text)
        await message.answer(f"Response: {assistant_response}")
        
        # Convert response to voice
        response_audio_path = f"audio_responses/{message.voice.file_id}_response.mp3"
        await openai_handler.text_to_speech(assistant_response, response_audio_path)
        
        # Send voice response
        await message.answer_voice(voice=types.FSInputFile(response_audio_path))
        
        # Remove temporary files
        os.remove(voice_path)
        os.remove(response_audio_path)
        
        # Delete processing message
        await processing_msg.delete()
        
    except Exception as e:
        logging.error(f"Error processing voice message: {e}")
        await message.answer("An error occurred while processing your voice message.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 
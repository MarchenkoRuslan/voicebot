# Voice AI Telegram Bot

A Telegram bot that can receive voice messages, convert them to text, get responses to questions, and voice the answers back to the user using the asynchronous OpenAI API client.

## Features

- Voice message to text conversion using Whisper API
- Natural language processing using OpenAI Assistant API
- Text to speech conversion using OpenAI TTS API
- Asynchronous processing of requests
- Temporary file cleanup

## Requirements

- Python 3.9+
- Telegram Bot Token
- OpenAI API Key

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/voice-ai-bot.git
   cd voice-ai-bot
   ```

2. Create and activate virtual environment:

   ```bash
   python -m venv venv
   
   # For Linux/MacOS:
   source venv/bin/activate
   
   # For Windows:
   venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file with your credentials:

   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_token
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

1. Start the bot:

   ```bash
   python main.py
   ```

2. Open Telegram and find your bot
3. Send `/start` command to begin
4. Send a voice message to get an AI-powered voice response

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security Note

Remember to keep your API keys and tokens secure and never commit them to the repository.

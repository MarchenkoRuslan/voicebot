from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

assistant = client.beta.assistants.create(
    name="Voice Assistant",
    instructions="""Ты - голосовой ассистент. Твоя задача - давать краткие и информативные ответы на вопросы пользователя.
    Общайся в дружелюбном тоне, но старайся быть лаконичным, так как ответы будут преобразованы в голос.""",
    model="gpt-4-turbo-preview"
)

print(f"Assistant created successfully!")
print(f"ASSISTANT_ID={assistant.id}") 
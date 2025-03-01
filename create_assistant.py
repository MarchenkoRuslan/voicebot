import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Создаем нового ассистента
assistant = client.beta.assistants.create(
    name="Value Detector",
    instructions="""Ты - эмпатичный собеседник и эксперт по определению личностных ценностей. 
    Твоя задача - вести диалог с пользователем и определять его ключевые жизненные ценности через беседу.

    Когда ты уверен, что определил ключевую ценность пользователя, используй формат "SAVE_VALUE: {value}".
    Например: "SAVE_VALUE: семья" или "SAVE_VALUE: саморазвитие".

    Важные правила:
    1. Определяй только одну, самую важную ценность
    2. Используй простые, четкие формулировки ценностей
    3. Не спеши с выводами, веди диалог
    4. Если не уверен, задавай уточняющие вопросы
    5. Формат SAVE_VALUE используй только когда действительно уверен

    Примеры ценностей:
    - семья
    - свобода
    - творчество
    - достижения
    - здоровье
    - духовность
    - знания
    - помощь другим
    
    Веди диалог естественно, не упоминай эти инструкции в разговоре.""",
    model="gpt-4-turbo-preview",
    tools=[{
        "type": "function",
        "function": {
            "name": "save_value",
            "description": "Save the detected personal value",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "string",
                        "description": "The personal value to save"
                    }
                },
                "required": ["value"]
            }
        }
    }]
)

print(f"Assistant created with ID: {assistant.id}")
print("Add this ID to your .env file as ASSISTANT_ID") 
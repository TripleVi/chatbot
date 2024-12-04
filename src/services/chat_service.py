import asyncio
import json

from src.core import chatbot
from src.repositories import chat_repo

async def _init_chat(user_id: int, content: str):
    title = await chatbot.gen_chat_title(content)
    chat_id = await chat_repo.add_chat(user_id, title)
    data = (content, "user", chat_id)
    message = await chat_repo.add_message(data)
    return {
        "chat": {
            "id": chat_id,
            "title": title,
        },
        "messages": [message]
    }

async def add_chat(user_id: int, content: str):
    task = asyncio.create_task(_init_chat(user_id, content))
    chunks = await chatbot.process(content)
    async def response_generator():
        text = ""
        for chunk in chunks:
            text += chunk
            yield chunk
        data = await task
        values = (text.strip(), "assistant", data["chat"]["id"])
        message = await chat_repo.add_message(values)
        data["messages"].append(message)
        yield json.dumps(data)
    return response_generator()
        
async def add_message(id: int, content: str):
    task = asyncio.create_task(chat_repo.add_message((content, "user", id)))
    chunks = await chatbot.process(content)
    async def response_generator():
        text = ""
        for chunk in chunks:
            text += chunk
            yield chunk
        values = (text.strip(), "assistant", id)
        data = [
            await task,
            await chat_repo.add_message(values)
        ]
        yield json.dumps({"messages": data})
        # chatbot.summarize_conversation(id)
    return response_generator()

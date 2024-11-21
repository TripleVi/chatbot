from src.core import chatbot
from src.repositories import chat_repo

def add_chat(user_id: int, content: str) -> int:
    title = chatbot.gen_chat_title(content)
    id = chat_repo.add_chat(user_id, title)
    response = chatbot.process(id, content)
    chat_repo.add_message(content=content, sender="user", chat_id=id)
    msg_id = chat_repo.add_message(content=response, sender="assistant", chat_id=id)
    return msg_id

def add_message(id: int, content: str) -> int:
    response = chatbot.process(id, content)
    chat_repo.add_message(content=content, sender="user", chat_id=id)
    msg_id = chat_repo.add_message(content=response, sender="assistant", chat_id=id)
    chatbot.summarize_conversation(id)
    return msg_id

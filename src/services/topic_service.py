from . import pinecone_service

from src.repositories import topic_repo
from src.core.error import CustomError

def handle_event(id: int, status: str):
    topic = topic_repo.get_topic(id, attributes=["id", "name"])
    if not topic:
        raise CustomError("TOPIC_NOT_EXIST")
    match status:
        case "created":
            on_topic_added(topic)
        case "updated":
            on_topic_updated(topic)
        case "deleted":
            on_topic_deleted(id)
        case _:
            raise ValueError("Invalid value!")

def on_topic_added(topic: dict):
    pinecone_service.add_proper_noun(topic["id"], topic["name"], "topic")

def on_topic_updated(topic: dict):
    pinecone_service.update_proper_noun(topic["id"], topic["name"], "topic")

def on_topic_deleted(id: int):
    pinecone_service.delete_proper_noun(id, "topic")

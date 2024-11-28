from . import pinecone_service

from src.repositories import topic_repo
from src.core.error import CustomError

async def handle_event(id: int, status: str):
    topic = await topic_repo.get_topic(id, attributes=["id", "name"])
    if not topic:
        raise CustomError("TOPIC_NOT_EXIST")
    match status:
        case "created":
            await on_topic_added(topic)
        case "updated":
            await on_topic_updated(topic)
        case "deleted":
            await on_topic_deleted(id)
        case _:
            raise ValueError("Invalid value!")

async def on_topic_added(topic: dict):
    await pinecone_service.add_proper_noun(topic["id"], topic["name"], "topic")

async def on_topic_updated(topic: dict):
    await pinecone_service.update_proper_noun(topic["id"], topic["name"], "topic")

async def on_topic_deleted(id: int):
    await pinecone_service.delete_proper_noun(id, "topic")

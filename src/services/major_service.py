from . import pinecone_service

from src.repositories import major_repo
from src.core.error import CustomError

async def handle_event(id: int, status: str):
    major = await major_repo.get_major(id, attributes=["id", "name"])
    if not major:
        raise CustomError("MAJOR_NOT_EXIST")
    match status:
        case "created":
            await on_major_added(major)
        case "updated":
            await on_major_updated(major)
        case "deleted":
            await on_major_deleted(id)
        case _:
            raise ValueError("Invalid value!")

async def on_major_added(major: dict):
    await pinecone_service.add_proper_noun(major["id"], major["name"], "major")

async def on_major_updated(major: dict):
    await pinecone_service.update_proper_noun(major["id"], major["name"], "major")

async def on_major_deleted(id: int):
    await pinecone_service.delete_proper_noun(id, "major")

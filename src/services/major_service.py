from . import pinecone_service

from src.repositories import major_repo
from src.core.error import CustomError

def handle_event(id: int, status: str):
    major = major_repo.get_major(id, attributes=["id", "name"])
    if not major:
        raise CustomError("MAJOR_NOT_EXIST")
    match status:
        case "created":
            on_major_added(major)
        case "updated":
            on_major_updated(major)
        case "deleted":
            on_major_deleted(id)
        case _:
            raise ValueError("Invalid value!")

def on_major_added(major: dict):
    pinecone_service.add_proper_noun(major["id"], major["name"], "major")

def on_major_updated(major: dict):
    pinecone_service.update_proper_noun(major["id"], major["name"], "major")

def on_major_deleted(id: int):
    pinecone_service.delete_proper_noun(id, "major")

import json

from . import pinecone_service

from src.repositories import project_repo
from src.core.error import CustomError

def handle_event(id: int, status: str):
    project = project_repo.get_project(
        id=id,
        attributes=["id", "title", "description", "year"]
    )
    if not project:
        raise CustomError("PROJECT_NOT_EXIST")
    sections = json.loads(project["description"])
    project["description"] = "\n\n".join([
        section["title"] + "\n" + section["content"]
        for section in sections
    ])
    project["authors"] = project_repo.get_authors(
        project_id=id,
        attributes=["name", "email"]
    )
    match status:
        case "created":
            on_project_added(project)
        case "updated":
            on_project_updated(project)
        case "deleted":
            on_project_deleted(id)
        case _:
            raise ValueError("Invalid value!")

def on_project_added(project: dict):
    pinecone_service.add_project(project)
    pinecone_service.add_proper_noun(project["id"], project["title"], "project_summary")

def on_project_updated(project: dict):
    pinecone_service.update_project(project)
    pinecone_service.update_proper_noun(project["id"], project["title"], "project_summary")

def on_project_deleted(id: int):
    pinecone_service.delete_project(id)
    pinecone_service.delete_proper_noun(id, "project_summary")

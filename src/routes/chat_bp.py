from operator import itemgetter

from flask import Blueprint, request

from src.services import chat_service

chat_bp = Blueprint("chat", __name__, url_prefix="/chats")

@chat_bp.route("/", methods=["POST"])
def create_chat():
    content, user_id = (
        itemgetter("content", "userId")(request.get_json())
    )
    try:
        message_id = chat_service.add_chat(user_id, content)
        return {"message_id": message_id}, 201
    except Exception as err:
        print(err)
        return "Internal Server Error", 500

@chat_bp.route("/<int:id>/messages", methods=["POST"])
def create_message(id):
    content = itemgetter("content")(request.get_json())
    try:
        message_id = chat_service.add_message(id, content)
        return {"message_id": message_id}, 201
    except Exception as err:
        print(err)
        return "Internal Server Error", 500

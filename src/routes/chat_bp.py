from operator import itemgetter

from quart import Blueprint, request

from src.services import chat_service

chat_bp = Blueprint("chat", __name__, url_prefix="/chats")

@chat_bp.route("", methods=["POST"])
async def create_chat():
    body = await request.get_json()
    content, user_id = itemgetter("content", "userId")(body)
    try:
        res_generator = await chat_service.add_chat(user_id, content)
        headers = {
            "Content-Type": "text/plain; charset=utf-8",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        }
        return res_generator, 201, headers
    except Exception as err:
        print(err)
        return "Internal Server Error", 500

@chat_bp.route("/<int:id>/messages", methods=["POST"])
async def create_message(id):
    body = await request.get_json()
    content = itemgetter("content")(body)
    try:
        res_generator = await chat_service.add_message(id, content)
        headers = {"content_type":"text/plain; charset=utf-8"}
        return res_generator(), 201, headers
    except Exception as err:
        print(err)
        return "Internal Server Error", 500

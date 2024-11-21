from operator import itemgetter

from flask import Blueprint, request

from src.services import topic_service
from src.core.error import CustomError

topic_bp = Blueprint("topic", __name__, url_prefix="/topics")

@topic_bp.route("/<int:id>", methods=["POST"])
def topic_handler(id):
    status = itemgetter("status")(request.get_json())
    try:
        topic_service.handle_event(id, status)
        return "No Content", 204
    except CustomError as err:
        match err.code:
            case "TOPIC_NOT_EXIST":
                return "Not Found", 404
            case _:
                raise
    except Exception as err:
        print(err)
        return "Internal Server Error", 500

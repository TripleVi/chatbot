from operator import itemgetter

from quart import Blueprint, request

from src.services import major_service
from src.core.error import CustomError

major_bp = Blueprint("major", __name__, url_prefix="/majors")

@major_bp.route("/<int:id>", methods=["POST"])
async def major_handler(id):
    body = await request.get_json()
    status = itemgetter("status")(body)
    try:
        await major_service.handle_event(id, status)
        return "No Content", 204
    except CustomError as err:
        match err.code:
            case "MAJOR_NOT_EXIST":
                return "Not Found", 404
            case _:
                raise
    except Exception as err:
        print(err)
        return "Internal Server Error", 500

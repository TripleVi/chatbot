from operator import itemgetter

from quart import Blueprint, request

from src.services import project_service
from src.core.error import CustomError

project_bp = Blueprint("project", __name__, url_prefix="/projects")

@project_bp.route("/<int:id>", methods=["POST"])
async def project_handler(id):
    body = await request.get_json()
    status = itemgetter("status")(body)
    try:
        await project_service.handle_event(id, status)
        return "No Content", 204
    except CustomError as err:
        match err.code:
            case "PROJECT_NOT_EXIST":
                return "Not Found", 404
            case _:
                raise
    except Exception as err:
        print(err)
        return "Internal Server Error", 500

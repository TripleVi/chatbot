from operator import itemgetter

from flask import Blueprint, request

from src.services import project_service
from src.core.error import CustomError

project_bp = Blueprint("project", __name__, url_prefix="/projects")

@project_bp.route("/<int:id>", methods=["POST"])
def project_handler(id):
    status = itemgetter("status")(request.get_json())
    try:
        project_service.handle_event(id, status)
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

from quart import Quart

from .major_bp import major_bp
from .topic_bp import topic_bp
from .project_bp import project_bp
from .chat_bp import chat_bp

def initRoutes(app: Quart):
    app.register_blueprint(major_bp)
    app.register_blueprint(topic_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(chat_bp)

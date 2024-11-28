import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from quart import Quart

from routes import initRoutes

app = Quart(__name__)

initRoutes(app)

if __name__ == "__main__":
    port = os.environ.get("PORT", 5000)
    app.run(port=port, debug=True)

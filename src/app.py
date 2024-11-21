import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from flask import Flask

from routes import initRoutes

load_dotenv()

app = Flask(__name__)

initRoutes(app)

if __name__ == "__main__":
    port = os.environ.get("PORT", 5000)
    app.run(port=port, debug=False)

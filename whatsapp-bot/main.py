from flask import Flask
from dotenv import load_dotenv
import os

from config import Config
from routes import register_routes

if os.path.exists(".env"):
    load_dotenv()
else:
    raise Warning("No .env file found. Please create one with the required environment variables.")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_routes(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5002, debug=True)

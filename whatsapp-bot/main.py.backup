from flask import Flask
from dotenv import load_dotenv
import os

from config import Config
from routes import register_routes
from routes.send import send_daily_prompt  # ✅ 你要定时执行的函数

if os.path.exists(".env"):
    load_dotenv()
else:
    raise Warning("No .env file found. Please create one with the required environment variables.")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_routes(app)

    # 添加一个首页路由，用于浏览器访问测试
    @app.route("/", methods=["GET"])
    def home():
        return "Flask WhatsApp Bot is running!"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

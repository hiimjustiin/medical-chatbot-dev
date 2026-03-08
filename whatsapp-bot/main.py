from flask import Flask
from dotenv import load_dotenv
import os

# 先加载 .env 文件，再导入其他模块
if os.path.exists(".env"):
    # 允许 .env 覆盖进程中已有的同名变量，避免读取到旧的系统环境变量
    load_dotenv(override=True)
else:
    raise Warning("No .env file found. Please create one with the required environment variables.")

from config import Config
from routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.url_map.strict_slashes = False  # ✅ 
    register_routes(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

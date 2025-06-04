from .send import send_bp
from .webhook import webhook_bp

def register_routes(app):
    app.register_blueprint(send_bp, url_prefix='/send')
    app.register_blueprint(webhook_bp, url_prefix='/webhook')

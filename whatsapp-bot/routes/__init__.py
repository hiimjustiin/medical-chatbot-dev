from .send import send_bp
from .webhook import webhook_bp
from .notifications import notifications_bp
from .rules import rules_bp

def register_routes(app):
    app.register_blueprint(send_bp, url_prefix='/send')
    app.register_blueprint(webhook_bp, url_prefix='/webhook')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(rules_bp, url_prefix='/rules')

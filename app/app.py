from flask import Flask
from .config import Config

# application factory function
def create_app():

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    from .extensions import db

    db.init_app(app)

    from .users import bp as user_bp
    from .models import bp as model_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(model_bp)

    return app

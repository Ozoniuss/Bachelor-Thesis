from flask import Flask
from .config import Config

import redis

jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)

# application factory function
def create_app():

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    from .extensions import db, bcrypt, jwt, cache, socketio, cors

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    cors.init_app(app)
    socketio.init_app(app)

    from .users import bp as user_bp
    from .models import bp as model_bp
    from .auth import bp as auth_bp
    from .services import bp as services_bp
    from .datasets import bp as datasets_bp
    from .trainings import bp as trainings_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(datasets_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(trainings_bp)

    return app

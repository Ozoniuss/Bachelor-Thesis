"""
Configure Settings for application for specific environment
"""
"""
TODOS:
- update response if jwt is missing
"""


from datetime import timedelta


class Config:
    """Common config options"""

    APPNAME = "OctoNN"
    VERSION = "1.0"
    # APPID = "fl_angular_docker"
    # SECRET_KEY = os.urandom(24)
    # TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_NATIVE_UNICODE = True
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    SECRET_KEY = "movethistoenvvaribale"

    # use env
    DB_NAME = "octonn_db"
    DB_USER = "octonn"
    DB_PASS = "sdh45walth27xndsk6"
    DB_ADDRESS = "localhost"
    DB_PORT = 5432

    JWT_SECRET_KEY = "ceipatrup4"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_TOKEN_LOCATION = "headers"

    CACHE_TYPE = "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 3000
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0
    CACHE_REDIS_URL = "redis://localhost:6379/0"
    # BROKER_URL = os.getenv("BROKER_URL") or "redis://localhost:6379/0"
    # CELERY_BACKEND = (
    #     os.getenv("CELERY_BACKEND")
    #     or "postgresql://postgres:postgres@localhost:5432/blogs_db"
    # )
    SQLALCHEMY_DATABASE_URI = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
        DB_USER, DB_PASS, DB_ADDRESS, DB_PORT, DB_NAME
    )

    # SOCK_SERVER_OPTIONS = {"ping_interval": 25}


# class DevelopmentConfig(Config):
#     """Dev environment config options"""

#     FLASK_ENV = "development"
#     DEBUG = True
#     # PROFILE = True


# class TestingConfig(Config):
#     """Testing environment config options"""

#     DEBUG = False
#     STAGING = True
#     TESTING = True
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     SQLALCHEMY_NATIVE_UNICODE = True
#     SQLALCHEMY_COMMIT_ON_TEARDOWN = True
#     BROKER_URL = "redis://localhost:6379/0"
#     CELERY_BACKEND = "postgresql://postgres:postgres@localhost:5432/blogs_db"
#     SQLALCHEMY_DATABASE_URI = "sqlite:///memory"


# class CeleryConfig(Config):
#     """Celery environment config options"""

#     FLASK_ENV = "development"
#     DEBUG = True
#     PROFILE = True


# class ProductionConfig(Config):
#     """Prod environment config options"""

#     FLASK_ENV = "production"
#     DEBUG = False
#     STAGING = False


# config = {
#     "development": DevelopmentConfig,
#     # "testing": TestingConfig,
#     # "celery": CeleryConfig,
#     # "production": ProductionConfig,
#     "default": DevelopmentConfig,
# }

from datetime import timedelta
from this import d
from flask import Blueprint, jsonify, request
from app.users.model import User
from app.extensions import db, bcrypt, jwt
from sqlalchemy.exc import (
    IntegrityError,
    NoResultFound,
)
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt,
)

from ..utils.filesystem import createUserDirectory
from ..public.api.exception import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)

from app import jwt_redis_blocklist

bp = Blueprint("auth", __name__, url_prefix="/auth")

ACCESS_EXPIRES = timedelta(days=30)

# Callback function to check if a JWT exists in the redis blocklist
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    err = UnauthorizedException(details="Token has expired.")
    return jsonify(errors=[err.as_dict()]), err.code


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    err = UnauthorizedException(details="Token has been revoked.")
    return jsonify(errors=[err.as_dict()]), err.code


@bp.post("/register")
def register_user():
    username = request.json["username"]
    password = request.json["password"]
    email = request.json["email"]
    encoded_pass = bcrypt.generate_password_hash(password).decode("utf-8")
    print(encoded_pass)
    user = User(username=username, password=encoded_pass, email=email)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        err = ConflictException(details="Username or email already exists.")
        return jsonify(errors=[err.as_dict()]), err.code

    # Creates a new directory for the user on the filesystem to store the models.
    createUserDirectory(user_id=str(user.id))

    return jsonify(), 200


@bp.post("/login")
def login_user():
    username = request.json.get("username")
    password = request.json.get("password")
    try:
        user = (
            db.session.query(User)
            .filter_by(
                username=username,
            )
            .one()
        )

    # Error messages are ambiguous for security purposes. Depending on how
    # much they annoy users this might not be ideal.
    except NoResultFound:
        err = NotFoundException("Invalid username or password.")
        return jsonify(errors=[err.as_dict()]), err.code

    if not bcrypt.check_password_hash(user.password, password):
        err = NotFoundException("Invalid username or password.")
        return jsonify(errors=[err.as_dict()]), err.code

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return (
        jsonify(
            {
                "data": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            }
        ),
        200,
    )


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return (
        jsonify(
            {
                "data": {
                    "access_token": access_token,
                }
            }
        ),
        200,
    )


@bp.delete("/logout")
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    jwt_redis_blocklist.set(jti, "", ex=int(ACCESS_EXPIRES.total_seconds()))
    return jsonify(
        data={"message": f"{ttype.capitalize()} token successfully revoked."}
    )

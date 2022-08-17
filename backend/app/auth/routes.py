from flask import Blueprint, jsonify, request
from app.users.model import User
from app.extensions import db, bcrypt
from sqlalchemy.exc import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound,
)
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from ..utils.filesystem import createUserDirectory

bp = Blueprint("auth", __name__, url_prefix="/auth")


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

        return (
            jsonify(
                errors=[
                    {"Detail": "Username or email already exists."},
                ]
            ),
            409,
        )

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

    # return 404 in any case to increase security
    except NoResultFound:
        return (
            jsonify(
                errors=[
                    {"Detail": "Invalid username or password."},
                ]
            ),
            404,
        )
    except MultipleResultsFound:
        return (
            jsonify(
                errors=[
                    {"Detail": "Two users with the same username exist"},
                ]
            ),
            500,
        )

    if not bcrypt.check_password_hash(user.password, password):
        return (
            jsonify(
                errors=[
                    {"Detail": "Invalid username or password"},
                ]
            ),
            404,
        )

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

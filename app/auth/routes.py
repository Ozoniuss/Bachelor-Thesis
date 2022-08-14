from flask import Blueprint, jsonify, request
from app.users.model import User
from app.extensions import db, bcrypt
from sqlalchemy.exc import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound,
)
from flask_jwt_extended import create_access_token

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.post("/register")
def register_user():
    username = request.json["username"]
    password = request.json["password"]
    email = request.json["email"]
    encoded_pass = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(username=username, password=encoded_pass, email=email)
    try:
        v = db.session.add(user)
        db.session.commit()
    except IntegrityError as e:

        return (
            jsonify(
                errors=[
                    {"Detail": "Username already exists"},
                ]
            ),
            409,
        )

    return jsonify(), 200


@bp.post("/login")
def login_user():
    print(type(request.json))
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
                    {"Detail": "Invalid username or password"},
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

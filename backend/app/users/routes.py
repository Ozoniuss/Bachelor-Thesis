from flask import Blueprint, jsonify
from .model import User
from flask_jwt_extended import jwt_required

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.get("/")
@jwt_required()
def list_users():

    all_users = User.query.all()

    return jsonify(data=[u.as_dict() for u in all_users])

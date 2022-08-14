from flask import Blueprint, jsonify
from .model import User

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.get("/")
def list_users():

    all_users = User.query.all()

    return jsonify(data=[u.as_dict() for u in all_users])

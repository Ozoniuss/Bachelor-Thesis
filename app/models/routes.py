from flask import Blueprint, jsonify
from .model import Model
from app.extensions import db

bp = Blueprint("models", __name__, url_prefix="/models")


@bp.get("/")
def list_models():
    try:
        all_models = Model.query.all()
        return jsonify(data=[m.as_dict() for m in all_models])
    except Exception as e:
        print(type(e))
        print(e)
        return jsonify({"a": "b"})

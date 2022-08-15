from flask import Blueprint, jsonify
from .model import Model
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from .resource import from_db_entity

bp = Blueprint("models", __name__, url_prefix="/models")

OCTONN_ADDRESS = "http://localhost:5000"


@bp.get("/")
@jwt_required()
def list_models():
    current_user_id = get_jwt_identity()
    model_data = []

    try:
        all_models = Model.query.filter(
            or_(
                Model.public == True,
                Model.uploader == current_user_id,
            )
        ).all()
        for m in all_models:
            model_data.append(from_db_entity(OCTONN_ADDRESS, m))
        return jsonify(data=model_data)
    except Exception as e:
        print(type(e))
        print(e)
        return jsonify(errors=[{"Detail": str(e)}])


@bp.patch("/")
@jwt_required()
def update_model():
    """
    Saves the current state of the model
    """
    pass


@bp.post("/")
@jwt_required()
def copy_model():
    """
    Creates a new model for the current user
    """

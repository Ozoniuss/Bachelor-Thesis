from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from .model import Training

bp = Blueprint("trainings", __name__, url_prefix="/models/<model_id>/trainings")


@bp.get("/")
@jwt_required()
def list_trainings(model_id):
    print(model_id)
    return jsonify(), 200


@bp.post("/")
@jwt_required()
def create_training(model_id):
    print(model_id)
    return jsonify(), 200

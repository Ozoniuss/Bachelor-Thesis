from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.trainings.resource import from_db_entity

from app.public.api.exception import NotFoundException
from .model import Training
from sqlalchemy.exc import NoResultFound, StatementError
from ..public.api.exception import BadRequestException

bp = Blueprint("trainings", __name__, url_prefix="/models/<model_id>/trainings")

OCTONN_ADDRESS = "http://localhost:5000"


@bp.get("/")
@jwt_required()
def list_trainings(model_id):
    print(model_id)
    return jsonify(), 200


@bp.get("/<training_id>")
@jwt_required()
def get_training(model_id, training_id):

    training: Training

    try:
        training = Training.query.filter_by(
            id=str(training_id), model=str(model_id)
        ).one()
    except StatementError:
        err = BadRequestException("Invalid uuid format.")
        return jsonify(errors=[err.as_dict()]), err.code
    except NoResultFound:
        err = NotFoundException("Training not found.")
        return jsonify(errors=[err.as_dict()]), err.code

    return jsonify(data=from_db_entity(OCTONN_ADDRESS, training)), 200

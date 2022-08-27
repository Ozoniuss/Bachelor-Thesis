from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.model import Model
from app.trainings.resource import from_db_entity

from .model import Training, get_id
from sqlalchemy.exc import NoResultFound, StatementError
from sqlalchemy import or_
from ..public.api.exception import BadRequestException, NotFoundException

from ..public.api import PaginationParams, get_pagination_links
from ..utils.sqlalchemy import List

bp = Blueprint("trainings", __name__, url_prefix="/models/<model_id>/trainings")

OCTONN_ADDRESS = "http://localhost:5000"


@bp.get("/")
@jwt_required()
def list_trainings(model_id):

    current_user = get_jwt_identity()
    # Access to the model is required to display trainings.
    try:
        _ = (
            Model.query.filter_by(id=model_id)
            .filter(or_(Model.belongs_to == current_user, Model.public == True))
            .one()
        )
    except NoResultFound:
        err = NotFoundException("Model not found.")
        return jsonify(errors=[err.as_dict()]), err.code

    args = request.args
    req_pag = PaginationParams(
        after=args.get("after", default="", type=str),
        before=args.get("before", default="", type=str),
        limit=args.get("limit", default=0, type=int),
    )
    order = args.get("order", default="desc", type=str)
    api_path = f"{OCTONN_ADDRESS}/models/{model_id}/trainings"

    result = []

    # Column needs to be unique, but due to the way trainings are created it is
    # guaranteed that is the case.
    col = Training.created_at
    query = Training.query.filter_by(model=model_id)

    all_trainings, prev, next = List(
        query=query,
        limit=req_pag.limit,
        cursorColumn=col,
        retrieveCursor=get_id,
        before=req_pag.before,
        after=req_pag.after,
        order=order,
    )

    for t in all_trainings:
        result.append(from_db_entity(OCTONN_ADDRESS, t))

        return jsonify(
            data=result,
            links=get_pagination_links(
                api_path=api_path,
                req_pagination_params=req_pag,
                next=next,
                prev=prev,
            ),
        )

    return jsonify(), 200


@bp.get("/<training_id>")
@jwt_required()
def get_training(model_id, training_id):

    current_user = get_jwt_identity()
    # Access to the model is required to display trainings.
    try:
        _ = (
            Model.query.filter_by(id=model_id)
            .filter(or_(Model.belongs_to == current_user, Model.public == True))
            .one()
        )
    except NoResultFound:
        err = NotFoundException("Model not found.")
        return jsonify(errors=[err.as_dict()]), err.code

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

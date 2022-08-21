from ast import Mod
from flask import Blueprint, jsonify, request, abort
from .model import Model
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from .resource import from_db_entity
from app.extensions import db
from sqlalchemy.exc import NoResultFound
from ..utils.filesystem import copyModel
from ..utils.env import MODELS_DIR
from ..utils.sqlalchemy import List
import json
import uuid
from .exceptions import PostModelBadArguments
from ..public.api import PaginationParams, get_pagination_links, ModelFilters
from ..public.api.exception import (
    BadRequestException,
    NotFoundException,
    InternalServerException,
)
from .model import get_id


bp = Blueprint("models", __name__, url_prefix="/models")


OCTONN_ADDRESS = "http://localhost:5000"


@bp.get("/")
@jwt_required()
def list_models():
    """
    Lists all models that the user has permission to see.

    If public is true, it lists all public models. If set to false, it lists
    all the private models of the user. If unset, it returns both public models
    and the user's private models.
    """
    current_user_id = get_jwt_identity()
    args = request.args
    req_pag = PaginationParams(
        after=args.get("after", default="", type=str),
        before=args.get("before", default="", type=str),
        limit=args.get("limit", default=0, type=int),
    )
    order = args.get("order", default="asc", type=str)
    filters = ModelFilters(
        name=args.get("name"),
        public=args.get("public"),
    )
    api_path = OCTONN_ADDRESS + "/models/"

    result = []

    col = Model.id
    query = Model.query

    if filters.public != None:
        query = query.filter(Model.public == filters.public)
    if filters.name != None:
        query = query.filter(Model.name == filters.name)

    # If there are no public filters, retrieve all the models that are either
    # the user's private models or public.
    if filters.public == None:
        query = query.filter(
            or_(Model.belongs_to == current_user_id, Model.public == True)
        )

    all_models, prev, next = List(
        query=query,
        limit=req_pag.limit,
        cursorColumn=col,
        retrieveCursor=get_id,
        before=req_pag.before,
        after=req_pag.after,
        order=order,
    )

    for m in all_models:
        result.append(from_db_entity(OCTONN_ADDRESS, m))

    return jsonify(
        data=result,
        links=get_pagination_links(
            api_path=api_path,
            req_pagination_params=req_pag,
            next=next,
            prev=prev,
        ),
    )


@bp.get("/<model_id>")
@jwt_required()
def get_model(model_id):

    model: Model
    current_user = get_jwt_identity()

    try:
        db.session(Model).query.filter_by(id=model_id).filter(
            or_(Model.belongs_to == current_user, Model.public == True)
        ).one()
    except NoResultFound:
        err = NotFoundException("Model not found.")
        return jsonify(errors=[err.as_dict()]), err.code

    return jsonify(data=from_db_entity(OCTONN_ADDRESS, model))


@bp.delete("/<model_id>")
@jwt_required()
def delete_model(model_id):

    updated_rows: int
    current_user = get_jwt_identity()

    try:
        updated_rows = (
            db.session()
            .query(Model)
            .filter(Model.id == model_id, Model.belongs_to == current_user)
            .delete()
        )
        db.session.commit()

    except Exception as e:
        err = InternalServerException(str(e))
        return jsonify(errors=[err.as_dict()]), err.code

    if updated_rows == 0:
        err = NotFoundException("Model not found.")
        return jsonify(errors=[err.as_dict()]), err.code

    return jsonify(), 200


@bp.patch("/<model_id>")
@jwt_required()
def update_model(model_id):

    model: Model
    current_user = get_jwt_identity()

    try:
        model = Model.query.filter_by(id=model_id).one()
    except NoResultFound:
        err = NotFoundException("Model not found.")
        return jsonify(errors=[err.as_dict()]), err.code

    # If the model does not belong to the user and is not public, they don't
    # have permission to see it. The error message is for security concerns.
    if (model.belongs_to != current_user) and (model.public == False):
        err = NotFoundException("Model not found.")
        return jsonify(errors=[err.as_dict()]), err.code

    pass


@bp.post("/")
@jwt_required()
def create_model():
    """
    Creates a new model for the current user
    """
    current_user_id = get_jwt_identity()

    from_file = request.files.get("from_file")
    from_copy = request.form.get("from_copy")

    try:
        validate_model_data(from_file, from_copy)
    except PostModelBadArguments as e:
        err = BadRequestException(str(e))
        return jsonify(errors=[err.as_dict()]), err.code

    if from_copy != None:
        model: Model
        try:
            model = db.session.query(Model).filter_by(id=from_copy).one()
        except NoResultFound:
            err = NotFoundException(f"Model not found.")
            return jsonify(errors=[err.as_dict()]), err.code

        # Do not allow making copies of models that are private to other users.
        if (model.belongs_to != current_user_id) and (model.public == False):
            err = NotFoundException(f"Model not found.")
            return jsonify(errors=[err.as_dict()]), err.code

        rand_uuid = str(uuid.uuid4())
        # The location where this model will get copied.
        new_location = f"{MODELS_DIR()}{str(current_user_id)}\{str(rand_uuid)}.h5"

        new_model = Model(
            id=rand_uuid,
            name=model.name,
            belongs_to=current_user_id,
            location=new_location,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            public=False,  # model is private when creating
            current_prediction_labels=model.current_prediction_labels,
        )

        db.session.add(new_model)
        db.session.commit()

        # Copy the architecture to the user's home directory.
        copyModel(model.location, new_model.location)

        return jsonify(data=from_db_entity(OCTONN_ADDRESS, new_model)), 201

    elif from_file != None:

        if not allowed_file(from_file.filename):
            err = BadRequestException("File extension not allowed, must be .h5")
            return jsonify(errors=[err.as_dict()]), err.code

        body_data = request.form.get("body")
        if body_data == None:
            err = BadRequestException(
                "Model details not specified, add them" + "with the body key."
            )
            return jsonify(errors=[err.as_dict()]), err.code

        body = json.loads(body_data)

        name = body.get("name")
        description = body.get("description")
        public = body.get("public")
        current_prediction_labels = body.get("current_prediction_labels")

        # The model identifier must be generated beforehand because a folder for
        # it must al
        rand_uuid = str(uuid.uuid4())
        location = f"{MODELS_DIR()}{str(current_user_id)}\{str(rand_uuid)}.h5"

        new_model = Model(
            id=rand_uuid,
            name=name,
            belongs_to=current_user_id,
            location=location,
            description=description,
            public=public,
            current_prediction_labels=current_prediction_labels,
        )

        db.session.add(new_model)
        db.session.commit()

        from_file.save(location)
        return jsonify(data=from_db_entity(OCTONN_ADDRESS, new_model)), 201


def validate_model_data(from_file, from_copy):
    if from_file == from_copy == None:
        raise PostModelBadArguments("No file or copy identifier provided.")

    if from_file != None and from_copy != None:
        raise PostModelBadArguments("Cannot use both a file and a copy identifier.")


ALLOWED_EXTENSIONS = ["h5"]


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

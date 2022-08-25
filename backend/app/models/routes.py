import uuid
from flask import Blueprint, jsonify, request
from .model import Model
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from .resource import from_db_entity
from app.extensions import db
from sqlalchemy.exc import NoResultFound
from ..utils.filesystem import (
    FileSystemException,
    copy_model,
    save_model_from_storage,
    must_remove_model,
)
from ..utils.file_extensions import allowed_file, get_model_allowed_extensions
from ..utils.sqlalchemy import List
import json
from .exceptions import PostModelBadArguments
from ..public.api import PaginationParams, get_pagination_links, ModelFilters
from ..public.api.exception import (
    BadRequestException,
    NotFoundException,
    InternalServerException,
)
from ..public.api.model import ModelMutableData
from .model import get_id
from keras.models import load_model as keras_load_model

from werkzeug.datastructures import FileStorage
import os
from keras import Sequential


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
        # specifying type=bool for this makes it always true for some reason
        # this can be None, true or false (str)
        public=args.get("public"),
    )
    api_path = OCTONN_ADDRESS + "/models/"

    result = []

    col = Model.id
    query = Model.query

    if filters.public != None:
        # Retrieve all public models.
        query = query.filter(Model.public == filters.public)

        # Retrieve only the private models of the user, not all private models.
        if filters.public == "false":
            query = query.filter(Model.belongs_to == current_user_id)
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
        model = (
            Model.query.filter_by(id=model_id)
            .filter(or_(Model.belongs_to == current_user, Model.public == True))
            .one()
        )
    except NoResultFound:
        err = NotFoundException("Model not found.")
        return jsonify(errors=[err.as_dict()]), err.code

    return jsonify(data=from_db_entity(OCTONN_ADDRESS, model))


@bp.delete("/<model_id>")
@jwt_required()
def delete_model(model_id):

    updated_rows: int
    current_user = get_jwt_identity()

    updated_rows = (
        db.session()
        .query(Model)
        .filter(Model.id == model_id, Model.belongs_to == current_user)
        .delete()
    )
    db.session.commit()

    if updated_rows == 0:
        err = NotFoundException("Model not found.")
        return jsonify(errors=[err.as_dict()]), err.code

    must_remove_model(model_id, current_user)

    return jsonify(), 200


@bp.patch("/<model_id>")
@jwt_required()
def update_model(model_id):

    current_user = get_jwt_identity()
    model: Model

    new_data = ModelMutableData(
        name=request.json.get("name"),
        description=request.json.get("description"),
        public=request.json.get("public"),
    )

    try:
        validate_update_params(new_data.name, new_data.description, new_data.public)
    except UpdateModelBadArguments as e:
        err = BadRequestException(details=str(e))
        return jsonify(errors=[err.as_dict()]), err.code

    try:
        model = Model.query.filter(
            Model.id == model_id, Model.belongs_to == current_user
        ).one()
    except NoResultFound:
        err = NotFoundException("Model not found.")
        return jsonify(errors=[err.as_dict()]), err.code

    if new_data.name != None:
        model.name = new_data.name
    if new_data.description != None:
        model.description = new_data.description
    if new_data.public != None:
        model.public = new_data.public
    db.session.commit()

    return jsonify(data=from_db_entity(OCTONN_ADDRESS, model)), 200


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

        new_model = Model(
            name=model.name,
            belongs_to=current_user_id,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            public=False,  # model is private when creating
            current_prediction_labels=model.current_prediction_labels,
            param_count=model.param_count,
        )

        db.session.add(new_model)
        db.session.commit()

        try:
            # Copy the architecture to the user's home directory.
            copy_model(
                old_model_id=model.id,
                old_user_id=model.belongs_to,
                new_model_id=new_model.id,
                new_user_id=new_model.belongs_to,
            )
        except FileSystemException as e:
            err = InternalServerException(str(e))
            return jsonify(errors=[err.as_dict()]), err.code

        return jsonify(data=from_db_entity(OCTONN_ADDRESS, new_model)), 201

    elif from_file != None:

        if not allowed_file(from_file.filename, get_model_allowed_extensions()):
            err = BadRequestException("File extension not allowed, must be .h5")
            return jsonify(errors=[err.as_dict()]), err.code

        body_data = request.form.get("body")
        if body_data == None:
            err = BadRequestException(
                "Model details not specified, add them " + "with the body key."
            )
            return jsonify(errors=[err.as_dict()]), err.code

        body = json.loads(body_data)

        name = body.get("name")
        description = body.get("description")
        current_prediction_labels = body.get("current_prediction_labels")

        # In addition, validate that the model is a keras model etc.
        network = read_model_from_file_storage(from_file)
        param_count = network.count_params()

        new_model = Model(
            name=name,
            belongs_to=current_user_id,
            description=description,
            public=False,
            current_prediction_labels=current_prediction_labels,
            param_count=param_count,
        )

        db.session.add(new_model)
        db.session.commit()

        save_model_from_storage(from_file, new_model.id, new_model.belongs_to)
        return jsonify(data=from_db_entity(OCTONN_ADDRESS, new_model)), 201


def validate_model_data(from_file, from_copy):
    if from_file == from_copy == None:
        raise PostModelBadArguments("No file or copy identifier provided.")

    if from_file != None and from_copy != None:
        raise PostModelBadArguments("Cannot use both a file and a copy identifier.")


class UpdateModelBadArguments(Exception):
    pass


def validate_update_params(name, description, public):
    if name == description == public == None:
        raise UpdateModelBadArguments(
            "At least one update parameter has to be specified."
        )


def read_model_from_file_storage(fs: FileStorage) -> Sequential:
    tmp_file = str(uuid.uuid4())
    fs.save(tmp_file)
    model = keras_load_model(tmp_file)
    os.remove(tmp_file)
    return model

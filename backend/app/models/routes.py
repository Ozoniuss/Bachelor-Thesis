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
from ..public.api.exception import BadRequestException, NotFoundException
from .model import get_id


bp = Blueprint("models", __name__, url_prefix="/models")


OCTONN_ADDRESS = "http://localhost:5000"


@bp.get("/")
@jwt_required()
def list_models():
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
    query = Model.query.filter(Model.belongs_to == current_user_id)

    if filters.public != None:
        query = query.filter(Model.public == filters.public)
    if filters.name != None:
        query = query.filter(Model.name == filters.name)

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


@bp.patch("/")
@jwt_required()
def update_model():
    """
    Saves the current state of the model
    """
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
            err = NotFoundException(f"Model {from_copy} not found.")
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

from tkinter.messagebox import NO
from flask import Blueprint, jsonify, request
from .model import Model
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from .resource import from_db_entity
from ..exceptions import PostModelBadArguments
from app.extensions import db
from sqlalchemy.exc import NoResultFound
from ..utils.filesystem import copyModel
from ..utils.env import MODELS_DIR
import json
import uuid

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
        return jsonify(errors=[e.as_dict()])

    if from_copy != None:
        model: Model
        try:
            model = db.session.query(Model).filter_by(id=from_copy).one()
        except NoResultFound:
            return (
                jsonify(
                    errors=[
                        {"Detail": f"Model with copy id {from_copy} does not exist."},
                    ]
                ),
                404,
            )

        rand_uuid = str(uuid.uuid4())
        # The location where this model will get copied.
        new_location = f"{MODELS_DIR()}{str(current_user_id)}\{str(rand_uuid)}.h5"

        new_model = Model(
            id=rand_uuid,
            name=model.name,
            uploader=model.uploader,
            location=new_location,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            public=False,  # model is originally private when copying
            current_prediction_labels=model.current_prediction_labels,
        )

        db.session.add(new_model)
        db.session.commit()

        # Copy the architecture to the user's home directory.
        copyModel(model.location, new_model.location)

        return jsonify(data=from_db_entity(OCTONN_ADDRESS, new_model)), 201

    elif from_file != None:

        if not allowed_file(from_file.filename):
            return (
                jsonify(
                    errors=[
                        PostModelBadArguments(
                            "Model file must have .h5 extension."
                        ).as_dict()
                    ]
                ),
                400,
            )

        body_data = request.form.get("body")
        if body_data == None:
            return (
                jsonify(errors=[PostModelBadArguments("No body found.").as_dict()]),
                400,
            )

        body = json.loads(body_data)

        name = body.get("name")
        description = body.get("description")
        public = body.get("public")
        current_prediction_labels = body.get("current_prediction_labels")

        rand_uuid = str(uuid.uuid4())
        location = f"{MODELS_DIR()}{str(current_user_id)}\{str(rand_uuid)}.h5"

        new_model = Model(
            id=rand_uuid,
            name=name,
            uploader=current_user_id,
            location=location,
            description=description,
            public=public,
            current_prediction_labels=current_prediction_labels,
        )

        db.session.add(new_model)
        db.session.commit()

        from_file.save(location)

        return jsonify(data=from_db_entity(OCTONN_ADDRESS, new_model)), 201

    else:
        return jsonify(
            errors=[
                {
                    "Title": "Server validation failed",
                    "Details": "Request parameters were not validated properly.",
                }
            ]
        )


def validate_model_data(from_file, from_copy):
    if from_file == from_copy == None:
        raise PostModelBadArguments("No file or copy identifier provided.")

    if from_file != None and from_copy != None:
        raise PostModelBadArguments("Cannot use both a file and a copy identifier.")


ALLOWED_EXTENSIONS = ["h5"]


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

from operator import or_
from urllib import request
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.model import Model
from ..public.api.exception import (
    BadRequestException,
    NotFoundException,
    InternalServerException,
)
from app.extensions import db, socketio
from sqlalchemy.exc import NoResultFound
import uuid

from sqlalchemy import or_
from ..utils.filesystem import (
    FileSystemException,
    load_model,
    remove_training_dataset,
    save_images_from_storage,
    remove_testing_dataset,
)
from ..utils.dataset_preparation import get_testing_dataset_iterators
from ..utils.file_extensions import get_image_allowed_extensions, allowed_file
from numpy import ndarray


bp = Blueprint("services", __name__, url_prefix="/services/<model_id>")


# For this operation we would ideally want to cache the stored model so that
# we can continuously make predictions. For now this would only load the model
# into memory and make a prediction on the input vector of images.
@bp.get("/prediction")
@jwt_required()
def make_prediction(model_id):

    current_user = get_jwt_identity()
    model: Model

    prediction_images = request.files.getlist("images")
    for img in prediction_images:
        if not allowed_file(img.filename, get_image_allowed_extensions()):
            err = BadRequestException("Image extension not allowed, must be .h5")
            return jsonify(errors=[err.as_dict()]), err.code

    test_folder = str(uuid.uuid4())

    try:
        save_images_from_storage(prediction_images, test_folder)
    except FileSystemException as e:
        err = InternalServerException(str(e))
        return jsonify(errors=[err.as_dict()]), err.code

    # This query is necessary in order to determine if the model is public or
    # not. It could be optimized by providing the user id asnd the model id
    # directly, but this is less secure because it doesn't take into account
    # the identity of the current user which means they could make predictions
    # with any private model.
    try:
        model = (
            Model.query.filter_by(id=model_id)
            .filter(or_(Model.belongs_to == current_user, Model.public == True))
            .one()
        )
    except NoResultFound:
        err = NotFoundException("Model not found.")
        remove_testing_dataset(test_folder)
        return jsonify(errors=[err.as_dict()]), err.code

    user_id = current_user
    if model.public == True:
        user_id = model.belongs_to

    network = load_model(model.id, user_id)
    test_ds = get_testing_dataset_iterators(test_folder)
    predictions: ndarray = network.predict(test_ds)

    remove_testing_dataset(test_folder)

    return (
        jsonify(
            data={
                "predictions": predictions.tolist(),
                "labels": model.current_prediction_labels,
            }
        ),
        200,
    )

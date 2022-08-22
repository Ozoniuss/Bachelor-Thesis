from operator import or_
from urllib import request
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.model import Model
from ..datasets.model import Dataset
from .perform_training import TrainingException, perform_training
from ..public.api.exception import (
    BadRequestException,
    NotFoundException,
    InternalServerException,
)
from app.extensions import db, socketio
from sqlalchemy.exc import NoResultFound
import uuid
import random

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


from .parameters import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_EPOCHS,
    DEFAULT_LEARNING_RATE,
    DEFAULT_ON_NOT_ENOUGH_SAMPLES,
    DEFAULT_SEED,
    DEFAULT_TRAIN_ALL_NETWORK,
    DEFAULT_VALIDATION_SPLIT,
    SEED,
    BATCH_SIZE,
    EPOCHS,
    LEARNING_RATE,
    ON_NOT_ENOUGH_SAMPLES,
    TRAIN_ALL_NETWORK,
    VALIDATION_SPLIT,
    SAMPLE_SIZE,
    DEFAULT_SAMPLE_SIZE,
    TrainingParametersException,
    validate_training_parameters,
)

bp = Blueprint("services", __name__, url_prefix="/services/<model_id>")


@bp.get("/training_params_validation")
@jwt_required()
def validate_params(model_id):
    """
    This function validates the training parameters specified by the user for
    training
    """
    args = request.args
    dataset_id = args.get("dataset_id", default=str(uuid.UUID(int=0)), type=str)

    epochs = args.get(EPOCHS, default=DEFAULT_EPOCHS, type=int)
    batch_size = args.get(BATCH_SIZE, default=DEFAULT_BATCH_SIZE, type=int)
    learning_rate = args.get(LEARNING_RATE, default=DEFAULT_LEARNING_RATE, type=float)
    sample_size = args.get(SAMPLE_SIZE, default=DEFAULT_SAMPLE_SIZE, type=int)
    on_not_enough_samples = args.get(
        ON_NOT_ENOUGH_SAMPLES, default=DEFAULT_ON_NOT_ENOUGH_SAMPLES, type=str
    )
    validation_split = args.get(
        VALIDATION_SPLIT, default=DEFAULT_VALIDATION_SPLIT, type=float
    )
    seed = args.get(SEED, default=DEFAULT_SEED, type=int)
    train_all_network = args.get(
        TRAIN_ALL_NETWORK, default=DEFAULT_TRAIN_ALL_NETWORK, type=bool
    )

    try:
        validate_training_parameters(
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            on_not_enough_samples=on_not_enough_samples,
            validation_split=validation_split,
            seed=seed,
        )
    except TrainingParametersException as e:
        err = BadRequestException(str(e))
        return (jsonify(errors=[err.as_dict()]), err.code)

    try:
        model = db.session.query(Model).filter_by(id=model_id).one()
    except NoResultFound:
        err = NotFoundException(f"Model {model_id} not found.")
        return jsonify(errors=[err.as_dict()]), err.code

    try:
        dataset = (db.session.query(Dataset).filter_by(id=dataset_id)).one()
    except NoResultFound:
        err = NotFoundException(f"Model {dataset_id} not found.")
        return jsonify(errors=[err.as_dict()]), err.code

    # The json returned here represents what should get passed to the server
    # through the "train" event via websockets, once the connection has been
    # established.
    return (
        jsonify(
            data={
                "model_id": model.id,
                "dataset_name": dataset.name,
                "model_labels": model.current_prediction_labels,
                "dataset_labels": dataset.labels,
                EPOCHS: epochs,
                BATCH_SIZE: batch_size,
                LEARNING_RATE: learning_rate,
                SAMPLE_SIZE: sample_size,
                ON_NOT_ENOUGH_SAMPLES: on_not_enough_samples,
                VALIDATION_SPLIT: validation_split,
                SEED: seed,
            }
        ),
        200,
    )


@bp.get("/training")
@jwt_required()
def train_model(model_id):

    args = request.args
    dataset_id = args.get("dataset_id", default=str(uuid.UUID(int=0)), type=str)
    epochs = args.get("epochs", default=10, type=int)
    batch_size = args.get("batch_size", default=10, type=int)
    learning_rate = args.get("learning_rate", default=0.0001, type=float)
    sample_size = args.get("sample_size", default=1000, type=int)
    on_not_enough_samples = args.get("on_not_enough_samples", default="error", type=str)
    validation_split = args.get("validation_split", default=0.2, type=float)
    seed = args.get("seed", default=random.randint(1, 256), type=int)

    try:
        validate_training_parameters(
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            on_not_enough_samples=on_not_enough_samples,
            validation_split=validation_split,
            seed=seed,
        )
    except TrainingParametersException as e:
        err = BadRequestException(str(e))
        return (jsonify(errors=[err.as_dict()]), err.code)

    model: Model
    dataset: Dataset

    try:
        model = db.session.query(Model).filter_by(id=model_id).one()
    except NoResultFound:
        err = NotFoundException(f"Model {model_id} not found.")
        return jsonify(errors=[err.as_dict()]), err.code

    try:
        dataset = (db.session.query(Dataset).filter_by(id=dataset_id)).one()
    except NoResultFound:
        err = NotFoundException(f"Model {dataset_id} not found.")
        return jsonify(errors=[err.as_dict()]), err.code

    try:
        history, out = perform_training(
            model_path=model.location,
            dataset_name=dataset.name,
            output_layer_size=0,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            sample_size=sample_size,
            on_not_enough_samples=on_not_enough_samples,
            validation_split=validation_split,
            seed=seed,
        )
    # Since this function creates the training dataset, it is only possible here
    # to determine if there were enough samples (if set to error).
    except TrainingParametersException as e:
        err = BadRequestException(str(e))
        return jsonify(errors=[err.as_dict()]), err.code
    except TrainingException as e:
        err = InternalServerException(str(e))
        return jsonify(errors=[err.as_dict()]), err.code

    return jsonify(results=history.history, output=out), 200


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

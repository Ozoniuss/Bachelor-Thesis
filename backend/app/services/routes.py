from json import JSONDecodeError
from urllib import request
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
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
    pass


# @sock.route("/echo")
# def echo(ws):
#     print("jaa")
#     while True:
#         data = ws.receive()
#         ws.send(data)

from urllib import request
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from .validate import validate_training_parameters, TrainingParametersException
from ..models.model import Model
from ..datasets.model import Dataset
from .perform_training import TrainingException, perform_training
from ..public.api.exception import (
    BadRequestException,
    NotFoundException,
    InternalServerException,
)
from app.extensions import db
from sqlalchemy.exc import NoResultFound
import uuid
import random

bp = Blueprint("services", __name__, url_prefix="/services/<model_id>")


@bp.get("/training")
@jwt_required()
def train_model(model_id):
    """
    This function trains a model on a specific dataset. The following are
    possible:
    - The model's current labels are the same as the dataset's labels. In this
    case, the output layer will stay the same and normal training shall be
    performed.
    - The model's current labels are different from the dataset's labels. This
    obviously includes not having the same number of neurons as the dataset's
    number of categories. In this case, the model will be loaded and the output
    layer will be removed and replaced by a new Dense (possibly customizable in
    the future) output layer with the required number of neurons. The new model
    shall be compiled and trained on the new dataset with the provided training
    configurations
    - It is possible to configure the following:
    - - epochs: limited to 30
    - - learning rate: between 0.1 and 0.0001 (adam compiler used)
    - - batch size: between 5 and 100
    - - on_not_enough_samples: see generateTrainingDataset definition
    - - validation_split: between 0 and 0.5. If set to 0 or not provided, there
    will be no validation dataset.
    - - seed: seed for shuffling the data. If not provided, it is generated
    automatically.

    It is desired that this becomes more configurable in the future. It should
    be at least possible to customize the loss function, the output layer type
    and the activation function of the output layer.
    """

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

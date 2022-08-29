from operator import or_
import uuid
from ..extensions import socketio, db
from .parameters import validate_training_parameters, TrainingParametersException
from flask_socketio import emit, send
from .training import (
    perform_training,
    prepare_dataset_iterators,
    load_model_in_memory,
    TrainingException,
    WebsocketCallback,
    DatasetPreparationException,
    LoadModelException,
)
from ..utils.filesystem import (
    FileSystemException,
    copy_model,
    must_remove_model,
    must_remove_training_dataset,
    save_model,
)
from flask import request
from flask import current_app
from app.extensions import cache
from ..models.model import Model
from ..datasets.model import Dataset
from sqlalchemy import or_
from sqlalchemy.exc import NoResultFound

from ..trainings.model import Training
from ..public.websocket.training_parameter import (
    from_dict,
)

from flask_jwt_extended import decode_token


@socketio.on("connect")
def connect_hander():
    current_app.logger.info(f"Ws client connected: {request.sid}")


@socketio.on("disconnect")
def disconnect_handler():
    sid = request.sid
    current_app.logger.info(f"Ws client disconnected: {sid}")
    must_remove_training_dataset(sid)

    user_id = cache.get(cache_user_id_key(sid))
    if user_id != None:
        must_remove_model(sid, user_id)

    clean_cache(sid)


@socketio.on("save_new")
def save_new_model(message):
    """
    This function saves the trained model as a new model in the databse.
    """
    sid = request.sid
    training: Training = cache.get(cache_training_key(sid))
    new_model: Model = cache.get(cache_new_db_model_key(sid))
    user_id = cache.get(cache_user_id_key(sid))
    if cache.get(sid) == None:
        emit(
            "error",
            "Training does not exist. Make sure training is still not in progress",
            to=sid,
        )
        return

    # Update the model specified in the training, since this will be a new model
    # and the training will correspond to the new model's history.
    training.model = new_model.id
    db.session.add(training)
    db.session.add(new_model)
    db.session.commit()

    # New model is saved in the user's directory in a file with the sid name.
    try:
        copy_model(sid, user_id, str(new_model.id), user_id)
    except FileSystemException as f:
        emit("error", str(f), to=sid)
        db.session.rollback()
        return

    emit("info", "Succesfully saved new model.", to=sid)

    must_remove_model(sid, user_id)
    clean_cache(sid)


@socketio.on("overwrite")
def overwrite_model(message):
    """
    This function overwrites a new trained model over an existing model.
    """
    sid = request.sid
    if cache.get(sid) == None:
        emit(
            "error",
            "Training does not exist. Make sure training is still not in progress",
            to=sid,
        )
        return

    training: Training = cache.get(cache_training_key(sid))
    old_model_id: Model = cache.get(cache_db_model_id_key(sid))
    new_model: Model = cache.get(cache_new_db_model_key(sid))
    user_id = cache.get(cache_user_id_key(sid))

    # Overwrite the existing model's details with the new ones computed after
    # training.
    from_db: Model = Model.query.filter(Model.id == old_model_id).one()

    from_db.last_trained_on = new_model.last_trained_on
    from_db.current_prediction_labels = new_model.current_prediction_labels
    from_db.param_count = new_model.param_count

    db.session.add(training)
    db.session.commit()

    # New model is saved in the user's directory in a file with the sid name.
    try:
        copy_model(sid, user_id, str(old_model_id), user_id, overwrite=True)
    except FileSystemException as f:
        emit("error", str(f), to=sid)
        db.session.rollback()
        return

    emit("info", "Model succesfully overwritten.", to=sid)

    must_remove_model(sid, user_id)
    clean_cache(sid)


@socketio.on("discard")
def discard_training(message):
    sid = request.sid
    training = cache.get(cache_training_key(sid))
    if training == None:
        emit(
            "error",
            "Training does not exist. Make sure training is still not in progress",
            to=sid,
        )
        return

    # Delete model from disk.
    user_id = cache.get(cache_user_id_key(sid))
    if user_id != None:
        must_remove_model(sid, user_id)

    # Delete caches.
    clean_cache(sid)
    emit("info", "Training succesfully discarded.")


@socketio.on("train")
def handle_training(msg):
    sid = request.sid

    message = from_dict(msg)
    authenticated_user_id: str

    try:
        token = decode_token(message.user_id)
        authenticated_user_id = token.get("sub")
        print(token)
        print(authenticated_user_id)
    except Exception:
        emit("error", "Invalid JWT token.", to=sid)

    if cache.get(sid) != None:
        emit("error", "Another training is waiting for completion.", to=sid)
        return

    cache.set(sid, "")

    try:
        validate_training_parameters(message.parameters)
    except TrainingParametersException as e:
        emit(
            "error",
            f"Invalid parameters: {str(e)}",
            to=sid,
        )
        return

    emit(
        "info",
        "Training parameters validated succesfully!",
        to=sid,
    )

    model_db: Model
    dataset_db: Dataset

    # get the model and the dataset from the database
    try:
        model_db = (
            Model.query.filter_by(id=message.model_id)
            .filter(
                or_(Model.belongs_to == authenticated_user_id, Model.public == True)
            )
            .one()
        )
    except NoResultFound:
        emit("error", f"Model {model_db} not found.", to=sid)
        return

    try:
        dataset_db = Dataset.query.filter_by(id=message.dataset_id).one()
    except NoResultFound:
        emit("error", f"Dataset {dataset_db} was not found.", to=sid)
        return

    history = out = None
    cb = WebsocketCallback(sid)

    # Creates folders
    try:
        train_ds, valid_ds, out = prepare_dataset_iterators(
            dataset_id=message.dataset_id,
            sample_size=message.parameters.sample_size,
            on_not_enough_samples=message.parameters.on_not_enough_samples,
            validation_split=message.parameters.validation_split,
            seed=message.parameters.seed,
            training_folder=sid,
        )
    except DatasetPreparationException as e:
        emit(
            "error",
            f"Could not prepare dataset for training: {str(e)}",
            to=sid,
        )
        return

    emit(
        "info",
        f"Number of images from each dataset: {out}",
        to=sid,
    )

    try:
        loaded_model = load_model_in_memory(
            message.model_id,
            user_id,
            model_db.current_prediction_labels,
            dataset_db.labels,
            message.parameters.train_all_network,
        )
    except LoadModelException as e:
        must_remove_training_dataset(sid)
        emit("error", {"data": str(e)}, to=sid)
        return

    try:
        model, history = perform_training(
            model=loaded_model,
            epochs=message.parameters.epochs,
            batch_size=message.parameters.batch_size,
            learning_rate=message.parameters.learning_rate,
            custom_callback=cb,
            train_ds=train_ds,
            valid_ds=valid_ds,
        )

    except TrainingException as e:
        must_remove_training_dataset(sid)
        emit("error", f"Could not perform training: {str(e)}", to=sid)
        return

    # Generate the training. For now it has the current model's uuid but if the
    # user decides to save this as a new model, it should be changed.
    training = Training(
        model=message.model_id,
        dataset=message.dataset_id,
        epochs=message.parameters.epochs,
        accuracy=history.history.get("accuracy"),
        loss=history.history.get("loss"),
        val_accuracy=history.history.get("val_accuracy"),
        val_loss=history.history.get("val_loss"),
    )

    new_model_uuid = uuid.uuid4()
    new_model_db = Model(
        id=str(new_model_uuid),
        name=model_db.name,
        belongs_to=authenticated_user_id,
        description=model_db.description,
        public=False,
        last_trained_on=message.dataset_id,
        current_prediction_labels=dataset_db.labels,
        param_count=model.count_params(),
    )

    init_cache(sid, authenticated_user_id, training, model_db.id, new_model_db)

    # Save the model temporarily in the user's director.
    save_model(model, sid, authenticated_user_id)

    emit("train_completed", "Training completed succesfully.", to=sid)

    # After training has completed, we can remove the training dataset from the
    # filesystem.
    must_remove_training_dataset(sid)
    return


def init_cache(sid, user_id, training, model_db_id, new_model_db):
    cache.set(cache_training_key(sid), training)
    cache.set(cache_db_model_id_key(sid), str(model_db_id))
    cache.set(cache_new_db_model_key(sid), new_model_db)
    cache.set(cache_user_id_key(sid), user_id)


def clean_cache(sid):
    cache.delete(cache_training_key(sid))
    cache.delete(cache_db_model_id_key(sid))
    cache.delete(cache_new_db_model_key(sid))
    cache.delete(cache_user_id_key(sid))
    cache.delete(sid)


def cache_training_key(sid: str) -> str:
    return f"training_{sid}"


def cache_db_model_id_key(sid: str) -> str:
    return f"model_db_{sid}"


def cache_new_db_model_key(sid: str) -> str:
    return f"new_model_db_{sid}"


def cache_user_id_key(sid: str) -> str:
    return f"user_id_{sid}"

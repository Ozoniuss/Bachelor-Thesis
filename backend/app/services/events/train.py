from distutils.command.clean import clean
from flask import request
from flask_socketio import emit
from flask_jwt_extended import decode_token

from sqlalchemy.exc import NoResultFound
import uuid

from .cache import cache_tip, cache_training, clean_cache, init_cache

from ...extensions import socketio, cache
from ...public.websocket.training_parameter import TrainModelMessage, from_dict
from ...public.websocket.channels import (
    TRAIN as TRAIN_CH,
    ERROR as ERROR_CH,
    INFO as INFO_CH,
)
from ..parameters import (
    validate_training_parameters,
    TrainingParametersException,
)
from ...utils.filesystem import must_remove_training_dataset, save_model

from ...models.model import Model
from ...datasets.model import Dataset
from ...trainings.model import Training


from ..training import (
    perform_training,
    prepare_dataset_iterators,
    load_model_in_memory,
    TrainingException,
    WebsocketCallback,
    DatasetPreparationException,
    LoadModelException,
)


@socketio.on(TRAIN_CH)
def handle_training(msg):
    sid = request.sid
    message: TrainModelMessage

    try:
        message = from_dict(msg)
    except Exception:
        emit(ERROR_CH, "Could not parse input message.", to=sid)
    authenticated_user_id: str

    try:
        token = decode_token(message.user_id)
        authenticated_user_id = token.get("sub")
    except Exception:
        emit(ERROR_CH, "Invalid JWT token.", to=sid)

    if cache.get(cache_tip(sid)) != None:
        emit(ERROR_CH, "Another training is currently in progress.", to=sid)
        return

    if cache.get(sid) != None:
        emit(ERROR_CH, "Cannot start another training until action.", to=sid)
        return

    # Set the caches to signify that training started and is in progress.
    cache.set(sid, "")
    cache.set(cache_tip(sid), "")

    try:
        validate_training_parameters(message.parameters)
    except TrainingParametersException as e:
        clean_cache(sid)
        emit(
            ERROR_CH,
            f"Invalid parameters: {str(e)}",
            to=sid,
        )
        return

    emit(
        INFO_CH,
        "Training parameters validated succesfully!",
        to=sid,
    )

    model_db: Model
    dataset_db: Dataset

    # get the model and the dataset from the database
    try:
        model_db = Model.query.filter_by(
            id=message.model_id, belongs_to=authenticated_user_id
        ).one()
    except NoResultFound:
        clean_cache(sid)
        emit(ERROR_CH, f"Model {model_db} not found.", to=sid)
        return

    try:
        dataset_db = Dataset.query.filter_by(id=message.dataset_id).one()
    except NoResultFound:
        clean_cache(sid)
        emit(ERROR_CH, f"Dataset {dataset_db} was not found.", to=sid)
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
        clean_cache(sid)
        emit(
            ERROR_CH,
            f"Could not prepare dataset for training: {str(e)}",
            to=sid,
        )
        return

    emit(
        INFO_CH,
        f"Number of images from each dataset: {out}",
        to=sid,
    )

    try:
        loaded_model = load_model_in_memory(
            message.model_id,
            authenticated_user_id,
            model_db.current_prediction_labels,
            dataset_db.labels,
            message.parameters.train_all_network,
        )
    except LoadModelException as e:
        clean_cache(sid)
        must_remove_training_dataset(sid)
        emit(ERROR_CH, str(e), to=sid)
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
        clean_cache(sid)
        must_remove_training_dataset(sid)
        emit(ERROR_CH, f"Could not perform training: {str(e)}", to=sid)
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

    # Save the model temporarily in the user's director.
    save_model(model, sid, authenticated_user_id)
    # After training has completed, we can remove the training dataset from the
    # filesystem.
    must_remove_training_dataset(sid)

    init_cache(sid, authenticated_user_id, training, model_db.id, new_model_db)
    cache.delete(cache_tip(sid))
    emit(INFO_CH, "Training completed succesfully.", to=sid)

    return

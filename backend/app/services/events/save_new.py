from flask import request
from flask_socketio import emit

from ...extensions import socketio, cache, db
from ...utils.filesystem import must_remove_model, copy_model, FileSystemException
from ...public.websocket.channels import ERROR as ERROR_CH, INFO as INFO_CH

from ...trainings.model import Training
from ...models.model import Model

from .cache import (
    cache_tip,
    cache_user_id,
    clean_cache,
    cache_training,
    cache_new_db_model,
)


@socketio.on("save_new")
def handle_save_new(message):
    """
    This function saves the trained model as a new model in the databse.
    """
    sid = request.sid

    if cache.get(cache_tip(sid)) != None:
        emit(ERROR_CH, "Training is currently in progress.", to=sid)
        return

    if cache.get(sid) == None:
        emit(
            ERROR_CH,
            "Training does not exist yet.",
            to=sid,
        )
        return

    training: Training = cache.get(cache_training(sid))
    new_model: Model = cache.get(cache_new_db_model(sid))
    user_id = cache.get(cache_user_id(sid))

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
        emit(ERROR_CH, str(f), to=sid)
        db.session.rollback()
        return

    emit(INFO_CH, "Succesfully saved new model.", to=sid)

    must_remove_model(sid, user_id)
    clean_cache(sid)

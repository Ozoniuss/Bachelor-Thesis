from flask import request
from flask_socketio import emit

from ...extensions import socketio, cache, db
from ...utils.filesystem import must_remove_model, copy_model, FileSystemException
from ...public.websocket.channels import ERROR as ERROR_CH, INFO as INFO_CH

from ...trainings.model import Training
from ...models.model import Model

from .cache import (
    cache_tip,
    cache_training,
    cache_user_id,
    clean_cache,
    cache_db_model_id,
    cache_new_db_model,
)


@socketio.on("overwrite")
def handle_overwrite(message):
    """
    This function overwrites a new trained model over an existing model.
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
    old_model_id: Model = cache.get(cache_db_model_id(sid))
    new_model: Model = cache.get(cache_new_db_model(sid))
    user_id = cache.get(cache_user_id(sid))

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
        emit(ERROR_CH, str(f), to=sid)
        db.session.rollback()
        return

    emit(INFO_CH, "Model succesfully overwritten.", to=sid)

    must_remove_model(sid, user_id)
    clean_cache(sid)

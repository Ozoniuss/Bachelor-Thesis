from flask import current_app, request

from ...extensions import socketio, cache
from ...utils.filesystem import must_remove_training_dataset, must_remove_model

from .cache import cache_tip, cache_user_id, clean_cache


@socketio.on("connect")
def connect_hander():
    current_app.logger.info(f"Ws client connected: {request.sid}")


@socketio.on("disconnect")
def disconnect_handler():
    sid = request.sid
    current_app.logger.info(f"Ws client disconnected: {sid}")
    must_remove_training_dataset(sid)

    user_id = cache.get(cache_user_id(sid))
    if user_id != None:
        must_remove_model(sid, user_id)

    cache.delete(cache_tip(sid))
    clean_cache(sid)

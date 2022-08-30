from flask import request
from flask_socketio import emit

from ...extensions import socketio, cache
from ...utils.filesystem import must_remove_model
from ...public.websocket.channels import ERROR as ERROR_CH, INFO as INFO_CH

from .cache import cache_tip, cache_training, cache_user_id, clean_cache


@socketio.on("discard")
def handle_discard(message):
    sid = request.sid
    training = cache.get(cache_training(sid))

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
    # Delete model from disk.
    user_id = cache.get(cache_user_id(sid))
    if user_id != None:
        must_remove_model(sid, user_id)

    # Delete caches.
    clean_cache(sid)
    emit("info", "Training succesfully discarded.")

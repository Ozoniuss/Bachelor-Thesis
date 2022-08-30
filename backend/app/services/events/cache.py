from ...extensions import cache


def init_cache(sid, user_id, training, model_db_id, new_model_db):
    cache.set(cache_training(sid), training)
    cache.set(cache_db_model_id(sid), str(model_db_id))
    cache.set(cache_new_db_model(sid), new_model_db)
    cache.set(cache_user_id(sid), user_id)


def clean_cache(sid):
    cache.delete(cache_training(sid))
    cache.delete(cache_db_model_id(sid))
    cache.delete(cache_new_db_model(sid))
    cache.delete(cache_user_id(sid))
    cache.delete(cache_tip(sid))
    cache.delete(sid)


def cache_training(sid: str) -> str:
    return f"training_{sid}"


def cache_db_model_id(sid: str) -> str:
    return f"model_db_{sid}"


def cache_new_db_model(sid: str) -> str:
    return f"new_model_db_{sid}"


def cache_user_id(sid: str) -> str:
    return f"user_id_{sid}"


# signifies that training is currently in progress
def cache_tip(sid: str) -> str:
    return f"tip_{sid}"

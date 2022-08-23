from ..extensions import socketio
from .parameters import validate_training_parameters, TrainingParametersException
from flask_socketio import emit, send
from .perform_training import perform_training, TrainingException, WebsocketCallback
from flask import request

from flask import current_app
from ..app import redis_db
from app.extensions import cache

from ..trainings.model import Training


@socketio.on("connect")
def connect_hander():
    current_app.logger.info(f"Ws client disconnected: {request.sid}")


@socketio.on("disconnect")
def disconnect_handler():
    current_app.logger.info("Ws client connected:", request.sid)


@socketio.on("train")
def handle_training(args):
    sid = request.sid

    # parameters should have already been validated using the validate endpoint
    model_id = args.get("model_id")
    user_id = args.get("user_id")
    dataset_id = args.get("dataset_id")
    model_labels = args.get("model_labels")
    dataset_labels = args.get("dataset_labels")
    epochs = args.get("epochs")
    batch_size = args.get("batch_size")
    learning_rate = args.get("learning_rate")
    sample_size = args.get("sample_size")
    on_not_enough_samples = args.get("on_not_enough_samples")
    validation_split = args.get("validation_split")
    seed = args.get("seed")
    train_all_network = args.get("train_all_network")

    history = out = None
    # This is more of a security concern, since parameters have already been
    # validated.
    try:
        validate_training_parameters(
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            on_not_enough_samples=on_not_enough_samples,
            validation_split=validation_split,
            seed=seed,
        )

    # This should never happen
    except TrainingParametersException as e:
        current_app.logger.error(
            f"Could not validate parameters, even though they "
            + f"shoul have already been validated: {str(e)}"
        )
        send("An error occured during server validation.")
        return

    cb = WebsocketCallback(sid)

    try:
        history, out = perform_training(
            model_id=model_id,
            user_id=user_id,
            dataset_id=str(dataset_id),
            model_labels=model_labels,
            dataset_labels=dataset_labels,
            epochs=epochs,
            batch_size=batch_size,
            sample_size=sample_size,
            learning_rate=learning_rate,
            on_not_enough_samples=on_not_enough_samples,
            validation_split=validation_split,
            seed=seed,
            train_all_network=train_all_network,
            custom_callback=cb,
            training_folder=sid,
        )

    except TrainingParametersException as e:
        current_app.logger.info(
            msg=f"Could not start training for client {sid}: {str(e)}"
        )
        send(str(e))
        return
    except TrainingException as e:
        current_app.logger.info(
            msg=f"An exception occured during training for client {sid}: {str(e)}"
        )
        send(str(e))
        return

    # training = Training(
    #     model=model_id,
    #     dataset=dataset_id,
    #     epochs=epochs,
    #     accuracy=history.history.get("acc")
    # )
    # cache.set(str(sid) + "_history", history.history)
    # print(cache.get(str(sid) + "_history"))

    print(history.history)
    print(out)

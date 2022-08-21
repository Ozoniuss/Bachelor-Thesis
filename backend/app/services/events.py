from ..extensions import socketio
from .parameters import validate_training_parameters, TrainingParametersException
from flask_socketio import emit, send
from .perform_training import perform_training, TrainingException
from flask import request

# Receive the test request from client and send back a test response
@socketio.on("hello")
def handle_message(data):
    print("received message: " + str(data))
    print(data)
    print(data["data"])


@socketio.on("connect")
def connect_hander():
    print(request.sid)


@socketio.on("disconnect")
def disconnect_handler():
    print(request.sid)
    print("fucking disconnected")


@socketio.on("train")
def handle_training(args):
    #     args = request.args

    # parameters should have already been validated using the validate endpoint
    client_id = args.get("client_id")
    dataset_id = args.get("dataset_id")
    epochs = args.get("epochs")
    batch_size = args.get("batch_size")
    learning_rate = args.get("learning_rate")
    sample_size = args.get("sample_size")
    on_not_enough_samples = args.get("on_not_enough_samples")
    validation_split = args.get("validation_split")
    seed = args.get("seed")

    history = out = None
    print(
        dataset_id,
        epochs,
        batch_size,
        learning_rate,
        sample_size,
        on_not_enough_samples,
        validation_split,
        seed,
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
        print(e)

    try:
        history, out = perform_training(
            client_id=client_id,
            model_path=r"C:\personal projects\Bachelor-Thesis\models\01232321-3222-2122-bb21-6a21abab1121\34a34a21-5671-0aa2-ff31-a2645cd12fe3.h5",
            dataset_name="cats-vs-dogs",
            output_layer_size=2,
            epochs=10,
            batch_size=10,
            sample_size=500,
            learning_rate=learning_rate,
            on_not_enough_samples="error",
            validation_split=0.2,
            seed=23,
        )

    except TrainingParametersException as e:
        print(e)
    except TrainingException as e:
        print(e)

    print(history)
    print(out)

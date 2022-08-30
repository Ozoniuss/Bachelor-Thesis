from typing import Union
from keras import Sequential
from keras.models import load_model
from keras.optimizers import adam_v2
from keras.losses import CategoricalCrossentropy
from keras.layers import Dense
from keras.callbacks import Callback
from ..utils.filesystem import (
    generate_training_dataset,
    FileSystemException,
)
from keras.callbacks import Callback
from ..extensions import socketio
from ..utils.list import same_labels
from ..utils.dataset_preparation import get_dataset_iterators
from ..utils.filesystem import load_model


class TrainingException(Exception):
    pass


class DatasetPreparationException(Exception):
    pass


class LoadModelException(Exception):
    pass


class WebsocketCallback(Callback):
    def __init__(self, sid):
        self.sid = sid

    def on_epoch_end(self, epoch, logs=None):
        stats = logs
        # For some reason epoch starts with 0.
        stats["epoch"] = epoch + 1
        socketio.emit("training_status", stats, to=self.sid)


def prepare_dataset_iterators(
    dataset_id,
    sample_size,
    on_not_enough_samples,
    training_folder,
    validation_split,
    seed,
):
    """
    This function prepares the model for training: it creates the training
    folder on the filesystem and the dataset iterators of that folder.

    The folders are added to the fileystem and must be cleaned up after
    training is completed.

    Returns the trainig dataset iterator, the validation iterator (if applicable)
    and a dictionary representing the number of images included for each label.
    """
    try:
        training_folder, out = generate_training_dataset(
            dataset_id=dataset_id,
            sample_size=sample_size,
            not_enough_samples=on_not_enough_samples,
            training_folder=training_folder,
        )
    # TODO: also catches errors non-related with the file system
    except FileSystemException as e:
        raise DatasetPreparationException(str(e))

    train_ds, valid_ds = get_dataset_iterators(training_folder, validation_split, seed)
    return train_ds, valid_ds, out


def load_model_in_memory(
    model_id, user_id, model_labels, dataset_labels, train_all_network
) -> Sequential:
    """Loads a model in memory as a keras sequential model, based on provided
    parameters."""
    model: Sequential = load_model(model_id, user_id)

    # Having the same labels means not changing the structure of the model, but
    # rather just performing additional training.
    if not same_labels(model_labels, dataset_labels):
        new_model = Sequential()
        for layer in model.layers[:-1]:
            new_model.add(layer)
        new_model.add(Dense(len(dataset_labels)))
        model = new_model

    # Set either all layers as trainable or only the last layer.
    if train_all_network:
        if model.count_params() > 20_000:
            raise LoadModelException(
                "Model cannot be trained entirely because it has too many"
                + "trainable params. This option is only available for models "
                + "with at most 20,000 parameters."
            )
        for idx, _ in enumerate(model.layers):
            model.layers[idx].trainable = True
    else:
        for idx, _ in enumerate(model.layers):
            model.layers[idx].trainable = False
        model.layers[len(model.layers) - 1].trainable = True

    return model


def perform_training(
    model: Sequential,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    custom_callback: Union[Callback, None],
    train_ds,
    valid_ds,
):

    history = None

    model.compile(
        optimizer=adam_v2.Adam(learning_rate=learning_rate),
        loss=CategoricalCrossentropy(),
        metrics="accuracy",
    )

    history = model.fit(
        train_ds,
        validation_data=valid_ds,
        epochs=epochs,
        batch_size=batch_size,
        callbacks=[custom_callback],
    )

    return model, history

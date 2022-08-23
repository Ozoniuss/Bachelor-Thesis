from typing import Union
from keras import Sequential
from keras.models import load_model
from keras.optimizers import adam_v2
from keras.losses import CategoricalCrossentropy
from keras.layers import Dense
from keras.callbacks import Callback
from ..utils.filesystem import (
    LABEL,
    ERROR,
    GLOBAL,
    generate_training_dataset,
    remove_training_dataset,
    FileSystemException,
)
from .parameters import TrainingParametersException
from keras.callbacks import Callback
from ..extensions import socketio
from ..utils.list import same_labels
from ..utils.dataset_preparation import get_dataset_iterators
from ..utils.filesystem import load_model
from contextlib import contextmanager


class TrainingException(Exception):
    pass


class WebsocketCallback(Callback):
    def __init__(self, sid):
        self.sid = sid

    def on_epoch_end(self, epoch, logs=None):
        stats = logs
        # For some reason epoch starts with 0.
        stats["epoch"] = epoch + 1
        socketio.emit("training_status", stats, to=self.sid)


# def with_training_dataset(dataset_id, sample_size, on_not_enough_samples):
#     training_folder = generate


def perform_training(
    model_id: str,
    user_id: str,
    dataset_id: str,
    model_labels: str,
    dataset_labels: str,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    sample_size: int,
    on_not_enough_samples: str,
    validation_split: float,
    seed: int,
    train_all_network: bool,
    custom_callback: Union[Callback, None],
    training_folder=None,
):
    """
    This function trains a model on a specific dataset. The following are
    possible:
    - The model's current labels are the same as the dataset's labels. In this
    case, the output layer will stay the same and normal training shall be
    performed.
    - The model's current labels are different from the dataset's labels. This
    obviously includes not having the same number of neurons as the dataset's
    number of categories. In this case, the model will be loaded and the output
    layer will be removed and replaced by a new Dense (possibly customizable in
    the future) output layer with the required number of neurons. The new model
    shall be compiled and trained on the new dataset with the provided training
    configurations.
    - It is possible to configure the following:
    - - epochs: limited to 30
    - - learning rate: between 0.1 and 0.0001 (adam compiler used)
    - - batch_size: between 5 and 100
    - - on_not_enough_samples: see generateTrainingDataset definition
    - - validation_split: between 0 and 0.5. If set to 0 or not provided, there
    will be no validation dataset.
    - - seed: seed for shuffling the data. If not provided, it is generated
    automatically.
    - - train_all_networks: whether to train the entire network or just the
    output layer. It shall be forbidden to train the entire network if the
    network is too large.

    It is desired that this becomes more configurable in the future. It should
    be at least possible to customize the loss function, the output layer type
    and the activation function of the output layer.
    """

    model: Sequential = load_model(model_id, user_id)
    history = None
    out = None

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
            raise TrainingParametersException(
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

    model.compile(
        optimizer=adam_v2.Adam(learning_rate=learning_rate),
        loss=CategoricalCrossentropy(),
        metrics="accuracy",
    )

    # This is the point where the dataset is added to the filesystem. The model
    # must then perform a cleanup operation.
    try:
        training_folder, out = generate_training_dataset(
            dataset_id=dataset_id,
            sample_size=sample_size,
            not_enough_samples=on_not_enough_samples,
            training_folder=training_folder,
        )
    except FileSystemException as e:
        raise TrainingParametersException(str(e))

    train_ds, valid_ds = get_dataset_iterators(training_folder, validation_split, seed)

    try:
        history = model.fit(
            train_ds,
            validation_data=valid_ds,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[custom_callback],
        )
    except Exception as e:
        raise TrainingException(str(e))
    finally:
        # Perform the cleanup operation.
        remove_training_dataset(training_folder)

    return history, out

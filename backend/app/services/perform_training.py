from statistics import mode
from keras import Sequential
from keras.models import load_model
from keras.optimizers import adam_v2
from keras.losses import CategoricalCrossentropy
from keras.utils import image_dataset_from_directory
from keras.layers import Rescaling, Dense
from ..utils.filesystem import (
    LABEL,
    ERROR,
    GLOBAL,
    generateTrainingDataset,
    removeTrainingDataset,
    FileSystemException,
)
from .parameters import TrainingParametersException
from keras.callbacks import Callback
from ..extensions import socketio
from ..utils.list import same_labels


class TrainingException(Exception):
    pass


class CustomCallback(Callback):
    def __init__(self, client_id):
        self.client_id = client_id

    def on_epoch_begin(self, epoch, logs=None):
        socketio.emit(self.client_id, "epoch fucking started")


def perform_training(
    client_id: str,
    model_path: str,
    dataset_name: str,
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

    model: Sequential = load_model(model_path)
    history = None
    out = None

    if not same_labels(model_labels, dataset_labels):
        new_model = Sequential()
        for layer in model.layers[:-1]:
            new_model.add(layer)
        new_model.add(Dense(len(dataset_labels)))
        model = new_model

    if train_all_network:
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

    try:

        training_path, out = generateTrainingDataset(
            dataset_name=dataset_name,
            sample_size=sample_size,
            not_enough_samples=on_not_enough_samples,
        )
    except FileSystemException as e:
        raise TrainingParametersException(str(e))

    train_ds = valid_ds = train_normalized_ds = valid_normalized_ds = None
    normalization_layer = Rescaling(1.0 / 255)

    # Setting this to 0 in image_dataset_from_directory return an error.
    if validation_split == 0:

        train_ds = image_dataset_from_directory(
            directory=training_path,
            labels="inferred",
            label_mode="categorical",
            seed=seed,
            color_mode="rgb",
            batch_size=10,
            image_size=(224, 224),
            subset="training",
            shuffle=True,
        )
        train_normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))

    else:
        train_ds = image_dataset_from_directory(
            directory=training_path,
            labels="inferred",
            label_mode="categorical",
            seed=seed,
            color_mode="rgb",
            batch_size=10,
            image_size=(224, 224),
            validation_split=validation_split,
            subset="training",
            shuffle=True,
        )
        train_normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))

        valid_ds = image_dataset_from_directory(
            directory=training_path,
            labels="inferred",
            label_mode="categorical",
            seed=seed,
            color_mode="rgb",
            batch_size=10,
            image_size=(224, 224),
            validation_split=validation_split,
            subset="validation",
            shuffle=True,
        )

        train_normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
        valid_normalized_ds = valid_ds.map(lambda x, y: (normalization_layer(x), y))

    try:
        history = model.fit(
            train_normalized_ds,
            validation_data=valid_normalized_ds,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[CustomCallback(client_id)],
        )
    except Exception as e:
        raise TrainingException(str(e))
    finally:
        removeTrainingDataset(training_path)

    return history, out

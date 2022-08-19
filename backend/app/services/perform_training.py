from keras import Sequential
from keras.models import load_model
from keras.optimizers import adam_v2
from keras.losses import SparseCategoricalCrossentropy
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
from .validate import TrainingParametersException


class TrainingException(Exception):
    pass


def perform_training(
    model_path: str,
    dataset_name: str,
    output_layer_size: str,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    sample_size: int,
    on_not_enough_samples: str,
    validation_split: float,
    seed: int,
):
    """
    Trains a model on a dataset, being provided the model path and the dataset
    name.
    """

    model: Sequential = load_model(model_path)
    history = None
    out = None

    # This is computed before calling this function. If positive, the model
    # will change its output layer.
    if output_layer_size > 0:
        new_model = Sequential()
        for layer in model.layers[:-1]:
            new_model.add(layer)
        new_model.add(Dense(output_layer_size))
        model = new_model

    model.compile(
        optimizer=adam_v2.Adam(learning_rate=learning_rate),
        loss=SparseCategoricalCrossentropy(from_logits=True),
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
            label_mode="int",
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
            label_mode="int",
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
            label_mode="int",
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
        )
    except Exception as e:
        raise TrainingException(str(e))
    finally:
        removeTrainingDataset(training_path)

    return history, out

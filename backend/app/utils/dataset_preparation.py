from keras.layers import Rescaling
from keras.utils import image_dataset_from_directory
from .filesystem import _get_training_path, _get_testing_path, FileSystemException


def __get_full_training_path(training_folder):
    """
    This is not ideal, but generating the directory iterators need to know some
    of the parameters which is not the filesystem's concern.

    However, the training location is isolated from the other important
    locations on the filesystem.
    """
    try:
        full_path = _get_training_path(training_folder)
        return full_path
    except FileNotFoundError:
        raise FileSystemException(
            "The training dataset was not found on the filesystem."
        )


def __get_full_testing_path(testing_folder):
    """
    This function is the equivalent of the above function, but for prediction
    datasets.
    """
    try:
        full_path = _get_testing_path(testing_folder)
        return full_path
    except FileNotFoundError:
        raise FileSystemException(
            "The testing dataset was not found on the filesystem."
        )


def get_dataset_iterators(training_folder, validation_split, seed):

    # could raise a file system exception
    training_path = __get_full_training_path(training_folder)

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

    return train_normalized_ds, valid_normalized_ds


def get_testing_dataset_iterators(testing_folder):

    full_path = __get_full_testing_path(testing_folder)

    test_ds = image_dataset_from_directory(
        directory=full_path,
        labels=None,
        label_mode="categorical",
        color_mode="rgb",
        batch_size=10,
        image_size=(224, 224),
    )
    # test_normalized_ds = test_ds.map(lambda x: normalization_layer(x))
    test_normalized_ds = test_ds
    return test_normalized_ds

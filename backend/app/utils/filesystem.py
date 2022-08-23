import os
import random
import uuid
import shutil
import glob
from werkzeug.datastructures import FileStorage
from keras.models import load_model as keras_load_model
from keras import Sequential

# todo: env variables
MODELS_DIR = "C:\personal projects\Bachelor-Thesis\models\\"
DATASETS_DIR = "C:\personal projects\Bachelor-Thesis\datasets\\"
TRAINING_DIR = "C:\personal projects\Bachelor-Thesis\\training\\"
TESTING_DIR = "C:\personal projects\Bachelor-Thesis\\test\\"

GLOBAL = "global"
LABEL = "label"
ERROR = "error"


class FileSystemException(Exception):
    pass


def _get_datasets_directory():
    return DATASETS_DIR


def _get_models_directory():
    return MODELS_DIR


def _get_user_path(user_id):
    full_path = os.path.join(MODELS_DIR, user_id)
    if not os.path.isdir(full_path):
        raise FileNotFoundError(f"{full_path} is not a valid user directory path.")
    return full_path


def _must_get_user_path(user_id):
    return os.path.join(MODELS_DIR, user_id)


def _get_model_path(model_id, user_id):
    full_path = f"{os.path.join(MODELS_DIR, user_id, model_id)}.h5"
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"{full_path} is not a valid model file path.")
    return full_path


def _must_get_model_path(model_id, user_id):
    return f"{os.path.join(MODELS_DIR, user_id, model_id)}.h5"


def _get_dataset_path(dataset_name):
    full_path = os.path.join(DATASETS_DIR, dataset_name)
    if not os.path.isdir(full_path):
        raise FileNotFoundError(f"{full_path} is not a valid dataset directory path.")
    return full_path


def _must_get_dataset_path(dataset_name):
    return os.path.join(DATASETS_DIR, dataset_name)


def _get_training_path(training_folder):
    full_path = os.path.join(TRAINING_DIR, training_folder)
    if not os.path.isdir(full_path):
        raise FileNotFoundError(f"{full_path} is not a valid training directory path.")
    return full_path


def _must_get_testing_path(testing_folder):
    return os.path.join(TESTING_DIR, testing_folder)


def _get_testing_path(testing_folder):
    full_path = os.path.join(TESTING_DIR, testing_folder)
    if not os.path.isdir(full_path):
        raise FileNotFoundError(f"{full_path} is not a valid testing directory path.")
    return full_path


def _must_get_training_path(training_folder):
    return os.path.join(TRAINING_DIR, training_folder)


def _get_dataset_label_path(dataset_name, label_name):
    full_path = os.path.join(DATASETS_DIR, dataset_name, label_name)
    if not os.path.isdir(full_path):
        raise FileNotFoundError(
            f"{full_path} is not a valid label directory path in dataset {dataset_name}."
        )
    return full_path


def _must_get_dataset_label_path(dataset_name, label_name):
    return os.path.join(DATASETS_DIR, dataset_name, label_name)


def _get_dataset_image_path(dataset_name, label_name, image_file):
    """The image file must be specified with extension."""
    full_path = os.path.join(DATASETS_DIR, dataset_name, label_name, image_file)
    if not os.path.isfile(full_path):
        raise FileNotFoundError(
            f"{full_path} is not a valid image file path in dataset {dataset_name}."
        )
    return full_path


def _must_get_dataset_image_path(dataset_name, label_name, image_file):
    return os.path.join(DATASETS_DIR, dataset_name, label_name, image_file)


def copy_model(old_model_id, old_user_id, new_model_id, new_user_id):
    """
    Throws an error if there already exists a file with the new
    model's identifier in the new user's directory.
    """
    try:
        old_path = _get_model_path(old_model_id, old_user_id)
    except FileNotFoundError:
        raise FileSystemException("Old model does not exist on the filesystem.")
    try:
        _get_user_path(new_user_id)
    except FileNotFoundError:
        raise FileSystemException("New user does not exist on the filesystem.")
    new_path = _must_get_model_path(new_model_id, new_user_id)
    print(new_path)

    if os.path.isfile(new_path):
        raise FileSystemException(
            "Cannot move model to new location because a file already exists there."
        )

    shutil.copy(old_path, new_path)


def save_model_from_storage(fs: FileStorage, model_id: str, user_id: str):
    full_path = _must_get_model_path(model_id, user_id)
    if os.path.isfile(full_path):
        raise FileSystemException(
            "Cannot save model from file storage to new location because a file already exists there."
        )
    try:
        fs.save(full_path)
    except Exception:
        raise FileSystemException("Could not save model from file storage.")


def save_images_from_storage(images: list[FileStorage], test_folder: str):
    full_path = _must_get_testing_path(test_folder)
    try:
        os.mkdir(full_path)
    except FileExistsError:
        raise FileSystemException(
            "Cannot save files from file storage to testing location because a"
            + "test dataset already exists there."
        )
    for img in images:
        try:
            img.save(os.path.join(full_path, img.filename))
        except Exception as e:
            print(e)
            raise FileSystemException("Could not save files from file storage.")


def create_user_directory(user_id: str):
    """Creates a directory for the new user in the models folder."""
    full_path = _must_get_user_path(user_id)
    try:
        os.mkdir(full_path)
    except FileExistsError:
        raise FileSystemException(f"User directory already exists on the file system.")


def generate_training_dataset(
    dataset_name: str,
    sample_size: int = 10,
    not_enough_samples=ERROR,
    training_folder=None,
):
    """
    Generates a training dataset for a specified dataset with a specified sample
    size for each category, on the filesystem.

    Each dataset is inside a directory labeled with the dataset's name, and the
    images for each label are inside a subdirectory with the label's name. This
    function will create a temporary directory labeled with a random uuid
    containing subdirectories for each label, and each subdirectory will contain
    "sample_size" number of images.

    Not enough samples is a parameter defined in the following way:
    - if set to "error", it throws an error if there is a label which doesn't
    have enough images to generate the sample
    - if set to "local", it uses all of the images in the directory to generate
    the training for a label, if the label has less images than the sample size
    - is set to "global", it does the same as above, except that all directories
    have the number of images, equal to the label with the least number of images.

    Returns the training path and an output dictionary containing the number of
    images from each category used in training.
    """
    try:
        dataset_path = _get_dataset_path(dataset_name)
    except FileNotFoundError:
        raise FileSystemException(
            f"Dataset {dataset_name} does not exist on the file system."
        )

    labels = os.listdir(dataset_path)

    # Generate a training folder with the name represented as a random uuid, or
    # with the identifier provided by the user. It is useful to provide an
    # identifier if using web sockets because it is easier to identify the
    # training dataset when closing the websocket connection.
    if training_folder == None:
        training_folder = str(uuid.uuid4())
    training_path = _must_get_training_path(training_folder)

    # Change of collision about 1 in 10e18, it is safe to assume this folder does not exist.
    try:
        os.mkdir(training_path)
    except FileExistsError:
        # easter egg :)
        raise FileSystemException(
            "There already exists a training taking place in this folder."
        )

    out = {}

    for label in labels:

        out[label] = 0

        images_path = os.path.join(training_path, label)
        os.mkdir(images_path)

        try:
            for img in random.sample(
                glob.glob(os.path.join(dataset_path, label, "*")), sample_size
            ):
                shutil.copy(img, images_path)

            out[label] = sample_size

        # There are not enough images
        except ValueError:
            if not_enough_samples == ERROR:
                shutil.rmtree(training_path)
                raise FileSystemException(f"Not enough samples for label {label}.")
            elif not_enough_samples == LABEL:
                for img in glob.glob(os.path.join(dataset_path, label, "*")):
                    shutil.copy(img, images_path)
                    out[label] += 1
            # TODO: global

    return (training_folder, out)


def remove_training_dataset(training_folder: str):
    try:
        training_path = _get_training_path(training_folder)
    except FileNotFoundError:
        raise FileSystemException(
            f"Training folder {training_folder} does not exist on the file system."
        )

    shutil.rmtree(training_path)


def must_remove_training_dataset(training_folder: str):
    training_folder = _must_get_training_path(training_folder)
    if os.path.isdir(training_folder):
        shutil.rmtree(training_folder)


def remove_testing_dataset(testing_folder: str):
    try:
        testing_path = _get_testing_path(testing_folder)
    except FileNotFoundError:
        raise FileSystemException(
            f"testing folder {testing_folder} does not exist on the file system."
        )

    shutil.rmtree(testing_path)


def must_remove_testing_dataset(testing_folder: str):
    testing_folder = _must_get_testing_path(testing_folder)
    if os.path.isdir(testing_folder):
        shutil.rmtree(testing_folder)


def get_labels_paginated(dataset_name: str, after: int = 0, limit: int = 0):
    """
    Returns the labels from a dataset, starting from the one on position
    specified by "after". Returns at most "limit" labels, or less if there
    aren't enough labels left. Set limit to 0 to get all the labels until the
    last one.

    This function basically returns the images found in the intersection of
    intervals [first_image, last_image] and [after, after + limit). It doesn't
    raise any errors if the second one is not strictly included in the first
    one.
    """
    try:
        full_path = _get_dataset_path(dataset_name)
    except FileNotFoundError:
        raise FileSystemException(
            f"Could not find dataset {dataset_name} on the file system."
        )
    next = 0
    if after + limit < len(os.listdir(full_path)):
        next = after + limit
    if limit != 0:
        return os.listdir(full_path)[after : after + limit], next
    else:
        return os.listdir(full_path)[after:], 0


def get_images_paginated(
    dataset_name: str, label_name: str, after: int = 0, limit: int = 0
) -> list[str]:
    """
    Returns the images from a dataset with a specific label. Behaves exactly
    like "getLabelsPaginated", see that function for documentation.
    """
    try:
        full_path = _get_dataset_label_path(dataset_name, label_name)
    except FileNotFoundError:
        raise FileSystemException(
            f"Could not find label {label_name} of dataset {dataset_name} on the file system."
        )
    glob_path = os.path.join(full_path, "*")
    next = 0
    if after + limit < len(glob.glob(glob_path)):
        next = after + limit
    if limit != 0:
        return glob.glob(glob_path)[after : after + limit], next
    else:
        return glob.glob(glob_path)[after:], 0


def load_model(model_id, user_id) -> Sequential:
    """
    Loads a model from the filesystem.
    """
    try:
        full_path = _get_model_path(model_id, user_id)
        return keras_load_model(full_path)
    except FileNotFoundError:
        raise FileSystemException("Model is not stored on the file system.")

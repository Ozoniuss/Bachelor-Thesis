import os
import random
import uuid
import shutil
import glob
import shutil

from .env import DATASETS_DIR, MODELS_DIR

GLOBAL = "global"
LABEL = "label"
ERROR = "error"


class FileSystemException(Exception):
    pass


def copyModel(src, dst):
    shutil.copy(src, dst)


def createUserDirectory(user_id: str):
    """Creates a directory for the new user in the models folder."""
    os.mkdir(f"{MODELS_DIR()}{user_id}")


def generateTrainingDataset(
    dataset_name: str,
    sample_size: int = 10,
    not_enough_samples=ERROR,
):
    """
    Generates a training dataset for a specified dataset with a specified sample
    size for each category.

    Each dataset is inside a directory labeled with the dataset's name, and the
    images for each label are inside a subdirectory with the label's name. This
    function will create a temporary directory labeled with a random uuid
    containing subdirectories for each label, and each subdirectory will contain
    "sample_size" number of images.

    Min sample size is a parameter defined in the following way:
    - if set to "error", it throws an error if there is a label which doesn't
    have enough images to generate the sample
    - if set to "local", it uses all of the images in the directory to generate
    the training for a label, if the label has less images than the sample size
    - is set to "global", it does the same as above, except that all directories
    have the number of images, equal to the label with the least number of images.

    Returns the training path and an output dictionary containing the number of
    images from each category used in training.
    """
    dataset_path = os.path.join(DATASETS_DIR(), dataset_name)

    labels = os.listdir(dataset_path)
    # generate a training folder with the name represented as a random uuid
    training_folder = str(uuid.uuid4())
    training_path = os.path.join(dataset_path, training_folder)
    os.mkdir(training_path)

    out = {}

    for label in labels:

        out[label] = 0

        images_path = os.path.join(training_path, label)
        os.mkdir(images_path)

        try:
            for img in random.sample(
                glob.glob(f"{dataset_path}/{label}/*"), sample_size
            ):
                shutil.copy(img, images_path)

            out[label] = sample_size

        # There are not enough images
        except ValueError:
            if not_enough_samples == ERROR:
                shutil.rmtree(training_path)
                raise FileSystemException(f"Not enough samples for label {label}.")
            elif not_enough_samples == LABEL:
                for img in glob.glob(f"{dataset_path}/{label}/*"):
                    shutil.copy(img, images_path)
                    out[label] += 1
            # TODO: global

    return (training_path, out)


def removeTrainingDataset(training_path: str):
    shutil.rmtree(training_path)


def getLabelsPaginated(dataset_name: str, after: int = 0, limit: int = 0) -> list[str]:
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
    full_path = os.path.join(DATASETS_DIR(), dataset_name)
    if limit != 0:
        return os.listdir(full_path)[after : after + limit]
    else:
        return os.listdir(full_path)[after:]


def getImagesPaginated(
    dataset_name: str, label_name: str, after: int = 0, limit: int = 0
) -> list[str]:
    """
    Returns the images from a dataset with a specific label. Behaves exactly
    like "getLabelsPaginated", see that function for documentation.
    """
    full_path = os.path.join(DATASETS_DIR(), dataset_name, label_name)
    glob_path = full_path + "\*"
    if limit != 0:
        return glob.glob(glob_path)[after : after + limit]
    else:
        return glob.glob(glob_path)[after:]

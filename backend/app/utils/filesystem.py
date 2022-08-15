import os
import random
import uuid
import shutil
import glob

DATASETS_DIR = os.getenv("OCTONN_DATASETS_PATH")

GLOBAL = "global"
LABEL = "label"
ERROR = "error"


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
    """
    dataset_path = os.path.join(DATASETS_DIR, dataset_name)

    labels = os.listdir(dataset_path)
    # generate a training folder with the name represented as a random uuid
    training_folder = uuid.uuid4().hex
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
        except ValueError as v:
            if not_enough_samples == ERROR:
                raise ValueError(v)
            elif not_enough_samples == LABEL:
                for img in glob.glob(f"{dataset_path}/{label}/*"):
                    shutil.copy(img, images_path)
                    out[label] += 1

    return (training_path, out)


def removeTrainingDataset(training_path: str):
    shutil.rmtree(training_path)
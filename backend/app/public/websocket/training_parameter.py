from dataclasses import dataclass

SAMPLES_LABEL = "label"
SAMPLES_ERROR = "error"

SEED = "seed"
BATCH_SIZE = "batch_size"
EPOCHS = "epochs"
LEARNING_RATE = "learning_rate"
VALIDATION_SPLIT = "validation_split"
ON_NOT_ENOUGH_SAMPLES = "on_not_enough_samples"
SAMPLE_SIZE = "sample_size"
TRAIN_ALL_NETWORK = "train_all_network"

DEFAULT_SEED = 0
DEFAULT_BATCH_SIZE = 32
DEFAULT_EPOCHS = 10
DEFAULT_LEARNING_RATE = 0.001
DEFAULT_VALIDATION_SPLIT = 0.2
DEFAULT_ON_NOT_ENOUGH_SAMPLES = "error"
DEFAULT_SAMPLE_SIZE = 1000
DEFAULT_TRAIN_ALL_NETWORK = False

MAX_SEED = 255
MIN_SEED = 0

MAX_BATCH_SIZE = 100
MIN_BATCH_SIZE = 1

MAX_EPOCHS = 30
MIN_EPOCHS = 1

MAX_LEARNING_RATE = 1
MIN_LEARNING_RATE = 0.0001

MAX_VALIDATION_SPLIT = 0.2
MIN_VALIDATION_SPLIT = 0.2

MAX_SAMPLE_SIZE = 5000
MIN_SAMPLE_SIZE = 1

ON_NOT_ENOUGH_SAMPLES_VALUES = [SAMPLES_LABEL, SAMPLES_ERROR]


@dataclass
class TrainingParameters:
    """
    Contains user-provided training parameters via websocket connection.

    parameters:
    - epochs: the number of times the entire dataset is processed. All training
    samples are processed in each epoch, in batches (if applicable).
    - batch_size: the number of samples processed before performing an
    optimization step of the training parameters. It is the same for all epochs.
    - learning_rate: a coefficient that multiplies the values (gradients) used
    to adjust the training parameters which were determined during an
    optimization step. Influences the "speed" of which the machine "learns".
    - sample_size: the number of samples for each label.
    - on_not_enough_samples: a  parameter that customizes the  application's
    behaviour if there are not enough samples from a label to match the sample
    size. Setting this to "labels" means that all available labels will be used,
    and setting it to "error" will throw an error and stop the execution.
    - validation_split: the ratio between the number of samples in the training
    and validation datasets. If set to 0, a validation dataset will not be
    generated
    - seed: a parameter that influences which images are used for training and
    which images are used for validation in the random selecting process. This
    is only useful if using all the images available; the same value will
    produce the same training and validation datasets.
    - train_all_network: tells whether the entire network should be trained or
    not. If set to false, only the output layer's trainable parameters will be
    adjusted.
    """

    epochs: int = DEFAULT_EPOCHS
    batch_size: int = DEFAULT_BATCH_SIZE
    learning_rate: float = DEFAULT_LEARNING_RATE
    sample_size: int = DEFAULT_SAMPLE_SIZE
    on_not_enough_samples: str = DEFAULT_ON_NOT_ENOUGH_SAMPLES
    validation_split: float = DEFAULT_VALIDATION_SPLIT
    seed: int = DEFAULT_SEED
    train_all_network: bool = DEFAULT_TRAIN_ALL_NETWORK


@dataclass
class TrainModelMessage:
    """
    Models the message sent via websocket to commence training.
    """

    model_id: str
    dataset_id: str
    user_id: str
    parameters: TrainingParameters


def from_dict(message) -> TrainModelMessage:
    return TrainModelMessage(
        model_id=message.get("model_id"),
        dataset_id=message.get("dataset_id"),
        user_id=message.get("user_id"),
        parameters=TrainingParameters(
            epochs=message.get("parameters").get(EPOCHS),
            batch_size=message.get("parameters").get(BATCH_SIZE),
            learning_rate=message.get("parameters").get(LEARNING_RATE),
            sample_size=message.get("parameters").get(SAMPLE_SIZE),
            on_not_enough_samples=message.get("parameters").get(ON_NOT_ENOUGH_SAMPLES),
            validation_split=message.get("parameters").get(VALIDATION_SPLIT),
            seed=message.get("parameters").get(SEED),
            train_all_network=message.get("parameters").get(TRAIN_ALL_NETWORK),
        ),
    )

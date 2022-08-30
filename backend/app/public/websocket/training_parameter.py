from dataclasses import dataclass

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


@dataclass
class TrainingParameters:
    """
    Contains user-provided training parameters via websocket connection.
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

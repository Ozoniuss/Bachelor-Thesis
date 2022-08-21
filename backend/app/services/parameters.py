from ..utils.filesystem import LABEL, GLOBAL, ERROR


class TrainingParametersException(Exception):
    pass


SEED = "seed"
BATCH_SIZE = "batch_size"
EPOCHS = "epochs"
LEARNING_RATE = "learning_rate"
VALIDATION_SPLIT = "validation_split"
ON_NOT_ENOUGH_SAMPLES = "on_not_enough_samples"
SAMPLE_SIZE = "sample_size"
TRAIN_ALL_NETWORK = "train_all_network"

DEFAULT_SEED = 3
DEFAULT_BATCH_SIZE = 32
DEFAULT_EPOCHS = 10
DEFAULT_LEARNING_RATE = 0.0001
DEFAULT_VALIDATION_SPLIT = 0.2
DEFAULT_ON_NOT_ENOUGH_SAMPLES = ERROR
DEFAULT_SAMPLE_SIZE = 1000
DEFAULT_TRAIN_ALL_NETWORK = False


def validate_training_parameters(
    epochs,
    batch_size,
    learning_rate,
    on_not_enough_samples,
    validation_split,
    seed,
):
    """
    Validates the training parameters passed as input to the perform_training
    function.
    """
    errors = ""
    if (seed > 256) or (seed < 1):
        errors += f"Invalid seed ({seed}): must be between 1 and 256\n"

    if (batch_size < 5) or (batch_size > 100):
        errors += f"Invalid batch size ({batch_size}): must be between 5 and 100\n"

    if epochs > 30:
        errors += f"Invalid number of epochs ({epochs}): must be less or equal to 30\n"

    if (learning_rate > 0.1) or (learning_rate < 0.0001):
        errors += (
            f"Invalid learning rate ({learning_rate}): must be between 0.0001 and 0.1\n"
        )

    if (validation_split < 0) or (validation_split > 0.5):
        errors += f"Invalid validation split ({validation_split}): must be between 0 (for no validation) and 0.5\n"

    if on_not_enough_samples not in [LABEL, GLOBAL, ERROR]:
        errors += f"Invalid behaviour if not enough samples ({on_not_enough_samples}): can only be LABEL, GLOBAL, ERROR\n"

    if errors != "":
        errors = errors.rstrip("\n")
        raise TrainingParametersException(errors)

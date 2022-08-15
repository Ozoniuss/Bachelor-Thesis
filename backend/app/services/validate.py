from ..exceptions import TrainingParametersException
from ..utils.filesystem import LABEL, GLOBAL, ERROR


def validate_training_parameters(
    epochs, batch_size, learning_rate, on_not_enough_samples, validation_split, seed
):
    if (seed > 256) or (seed < 1):
        raise TrainingParametersException(
            f"Invalid seed {seed}: must be between 1 and 256"
        )
    if (batch_size < 5) or (batch_size > 100):
        raise TrainingParametersException(
            f"Invalid batch size {batch_size}: must be between 5 and 100"
        )
    if epochs > 30:
        raise TrainingParametersException(
            f"Invalid number of epochs {epochs}: must be less or equal to 30"
        )

    if (learning_rate > 0.1) or (learning_rate < 0.0001):
        raise TrainingParametersException(
            f"Invalid learning rage {learning_rate}: must be between 0.0001 and 0.1"
        )

    if (validation_split < 0) or (validation_split > 0.5):
        raise TrainingParametersException(
            f"Invalid validation split {validation_split}: must be between 0 (for no validation) and 0.5"
        )

    if on_not_enough_samples not in [LABEL, GLOBAL, ERROR]:
        raise TrainingParametersException(
            f"Invalid behaviour if not enough samples {on_not_enough_samples}: can only be LABEL, GLOBAL, ERROR"
        )

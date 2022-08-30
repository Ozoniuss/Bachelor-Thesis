from ..public.websocket.training_parameter import (
    TrainingParameters,
    MAX_BATCH_SIZE,
    MAX_EPOCHS,
    MAX_LEARNING_RATE,
    MAX_SAMPLE_SIZE,
    MAX_SEED,
    MAX_VALIDATION_SPLIT,
    MIN_BATCH_SIZE,
    MIN_SAMPLE_SIZE,
    MIN_EPOCHS,
    MIN_LEARNING_RATE,
    MIN_SEED,
    MIN_VALIDATION_SPLIT,
    ON_NOT_ENOUGH_SAMPLES_VALUES,
)


class TrainingParametersException(Exception):
    pass


def validate_training_parameters(params: TrainingParameters):
    """
    Validates the training parameters passed as input to the perform_training
    function.
    """
    errors = ""
    if (params.seed > MAX_SEED) or (params.seed < MIN_SEED):
        errors += f"Invalid seed ({params.seed}): must be between {MIN_SEED} and {MAX_SEED}.\n"

    if (params.batch_size < MIN_BATCH_SIZE) or (params.batch_size > MAX_BATCH_SIZE):
        errors += f"Invalid batch size ({params.batch_size}): must be between {MIN_BATCH_SIZE} and {MAX_BATCH_SIZE}.\n"

    if (params.epochs < MIN_EPOCHS) or (params.epochs > MAX_EPOCHS):
        errors += f"Invalid number of epochs ({params.epochs}): must be between {MIN_EPOCHS} and {MAX_EPOCHS}.\n"

    if (params.sample_size < MIN_SAMPLE_SIZE) or (params.sample_size > MAX_SAMPLE_SIZE):
        errors += f"Invalid sample size ({params.sample_size}): must be between {MIN_SAMPLE_SIZE} and {MAX_SAMPLE_SIZE}.\n"

    if (params.learning_rate > MAX_LEARNING_RATE) or (
        params.learning_rate < MIN_LEARNING_RATE
    ):
        errors += f"Invalid learning rate ({params.learning_rate}): must be between {MIN_LEARNING_RATE} and {MAX_LEARNING_RATE}.\n"

    if (params.validation_split < MIN_VALIDATION_SPLIT) or (
        params.validation_split > MAX_VALIDATION_SPLIT
    ):
        errors += f"Invalid validation split ({params.validation_split}): must be between {MIN_VALIDATION_SPLIT} (for no validation) and {MAX_VALIDATION_SPLIT}.\n"

    if params.on_not_enough_samples not in ON_NOT_ENOUGH_SAMPLES_VALUES:
        errors += f"Invalid behaviour if not enough samples ({params.on_not_enough_samples}): must be one of {','.join(ON_NOT_ENOUGH_SAMPLES_VALUES)}.\n"

    if errors != "":
        errors = errors.rstrip("\n")
        raise TrainingParametersException(errors)

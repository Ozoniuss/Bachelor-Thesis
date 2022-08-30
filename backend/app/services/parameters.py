from ..utils.filesystem import LABEL, GLOBAL, ERROR
from ..public.websocket.training_parameter import TrainingParameters


class TrainingParametersException(Exception):
    pass


def validate_training_parameters(params: TrainingParameters):
    """
    Validates the training parameters passed as input to the perform_training
    function.
    """
    errors = ""
    if (params.seed > 256) or (params.seed < 0):
        errors += f"Invalid seed ({params.seed}): must be between 0 and 256.\n"

    if (params.batch_size < 5) or (params.batch_size > 100):
        errors += (
            f"Invalid batch size ({params.batch_size}): must be between 5 and 100.\n"
        )

    if params.epochs > 30:
        errors += f"Invalid number of epochs ({params.epochs}): must be less or equal to 30.\n"

    if (params.learning_rate > 0.1) or (params.learning_rate < 0.0001):
        errors += f"Invalid learning rate ({params.learning_rate}): must be between 0.0001 and 0.1.\n"

    if (params.validation_split < 0) or (params.validation_split > 0.5):
        errors += f"Invalid validation split ({params.validation_split}): must be between 0 (for no validation) and 0.5.\n"

    if params.on_not_enough_samples not in [LABEL, GLOBAL, ERROR]:
        errors += f"Invalid behaviour if not enough samples ({params.on_not_enough_samples}): can only be LABEL, GLOBAL, ERROR.\n"

    if errors != "":
        errors = errors.rstrip("\n")
        raise TrainingParametersException(errors)

from flask import Blueprint
from flask_jwt_extended import jwt_required

bp = Blueprint("services", __name__, url_prefix="/services")


@bp.get("/train/<model_id>")
@jwt_required()
def train_model():
    pass


# For this operation we would ideally want to cache the stored model so that
# we can continuously make predictions. For now this would only load the model
# into memory and make a prediction on the input vector of images.
@bp.get("/predict/<model_id>")
@jwt_required()
def make_prediction():
    pass

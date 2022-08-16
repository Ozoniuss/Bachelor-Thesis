from flask import Blueprint, jsonify
from .model import Dataset
from flask_jwt_extended import jwt_required
from .resource import from_db_entity

bp = Blueprint("datasets", __name__, url_prefix="/datasets")

OCTONN_ADDRESS = "http://localhost:5000"


# This operation might not require authentication
@bp.get("/")
@jwt_required()
def list_datasets():
    datasets = []
    try:
        all_datasets = Dataset.query.all()
        for d in all_datasets:
            datasets.append(from_db_entity(OCTONN_ADDRESS, d))
        return jsonify(data=datasets)
    except Exception as e:
        return jsonify(errors=[{"Detail": str(e)}])

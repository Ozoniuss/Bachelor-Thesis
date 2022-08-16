from email.policy import default
from flask import Blueprint, jsonify, request
from .model import Dataset
from flask_jwt_extended import jwt_required
from .resource import from_db_entity
from ..utils.sqlalchemy import List, ASC, DESC
from ..utils.resource import PaginationParams, get_pagination_links
from .model import get_id

bp = Blueprint("datasets", __name__, url_prefix="/datasets")

OCTONN_ADDRESS = "http://localhost:5000"


# This operation might not require authentication
@bp.get("/")
@jwt_required()
def list_datasets():

    args = request.args
    req_pag = PaginationParams(
        after=args.get("after", default="", type=str),
        before=args.get("before", default="", type=str),
        limit=args.get("limit", default=0, type=int),
    )
    print(req_pag)
    order = args.get("order", default="asc", type=str)
    api_path = OCTONN_ADDRESS + "/datasets/"

    result = []

    try:
        query = Dataset.query
        col = Dataset.id

        all_datasets, prev, next = List(
            query=query,
            limit=req_pag.limit,
            cursorColumn=col,
            retrieveCursor=get_id,
            before=req_pag.before,
            after=req_pag.after,
            order=order,
        )

        for d in all_datasets:
            result.append(from_db_entity(OCTONN_ADDRESS, d))

        return jsonify(
            data=result,
            links=get_pagination_links(
                api_path=api_path,
                req_pagination_params=req_pag,
                next=next,
                prev=prev,
            ),
        )
    except Exception as e:
        return jsonify(errors=[{"Detail": str(e)}])

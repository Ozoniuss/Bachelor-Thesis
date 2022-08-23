from flask import Blueprint, jsonify, request, session
from .model import Dataset, get_id
from flask_jwt_extended import jwt_required
from .resource import from_db_entity
from ..utils.sqlalchemy import List, ASC, DESC
from ..utils.filesystem import get_labels_paginated, get_images_paginated
from ..public.api.pagination import PaginationParams, get_pagination_links
from ..public.api.folder_pagination import (
    PaginationParams as FolderPaginationParams,
    get_pagination_links as get_folder_pagination_links,
)
from ..public.api.exception import NotFoundException
from sqlalchemy.exc import NoResultFound
from ..extensions import db

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
    order = args.get("order", default="asc", type=str)
    api_path = OCTONN_ADDRESS + "/datasets/"

    result = []

    query = Dataset.query
    col = Dataset.name

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


@bp.get("/<dataset_id>/labels")
@jwt_required()
def list_labels(dataset_id):

    try:
        dataset = db.session.query(Dataset).filter_by(id=dataset_id).one()
    except NoResultFound:
        err = NotFoundException("Invalid dataset uuid.")
        return jsonify(errors=[err.as_dict()]), err.code

    args = request.args
    req_pag = FolderPaginationParams(
        after=args.get("after", default=0, type=int),
        limit=args.get("limit", default=0, type=int),
    )
    api_path = OCTONN_ADDRESS + f"/datasets/{dataset_id}/labels"

    result, next = get_labels_paginated(dataset.id, req_pag.after, req_pag.limit)
    print(next)

    return jsonify(
        data=result,
        links=get_folder_pagination_links(
            api_path=api_path,
            req_pagination_params=req_pag,
            next=next,
        ),
    )


@bp.get("/<dataset_id>/labels/<label_name>/images")
@jwt_required()
def list_images(dataset_id, label_name):

    try:
        dataset = db.session.query(Dataset).filter_by(id=dataset_id).one()
    except NoResultFound:
        err = NotFoundException("Invalid dataset uuid.")
        return jsonify(errors=[err.as_dict()]), err.code

    args = request.args
    req_pag = FolderPaginationParams(
        after=args.get("after", default=0, type=int),
        limit=args.get("limit", default=0, type=int),
    )
    api_path = OCTONN_ADDRESS + f"/datasets/{dataset_id}/labels/{label_name}/images"

    result, next = get_images_paginated(
        dataset.id, label_name, req_pag.after, req_pag.limit
    )
    print(next)

    return jsonify(
        data=result,
        links=get_folder_pagination_links(
            api_path=api_path,
            req_pagination_params=req_pag,
            next=next,
        ),
    )

"""
Contains the resource model
"""

from dataclasses import dataclass
from typing import Union
import uuid
from .model import Model


@dataclass
class Links:
    self: Union[str, None] = None
    related: Union[str, None] = None


@dataclass
class ModelAttributes:
    name: str
    description: str
    created_at: str
    updated_at: str
    public: bool


@dataclass
class ModelMeta:
    current_prediction_labels: list[str]


@dataclass
class ModelRelationships:
    uploader: Links
    last_trained_on: Union[Links, None] = None


@dataclass
class ModelData:
    id: uuid.UUID
    attributes: ModelAttributes
    meta: ModelMeta
    links: Links
    relationships: ModelRelationships
    type: str = "model"


def from_db_entity(url: str, entity: Model):

    data = ModelData(
        id=entity.id,
        attributes=ModelAttributes(
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            public=entity.public,
        ),
        links=Links(self=url + "/model/" + str(entity.id)),
        meta=ModelMeta(current_prediction_labels=entity.current_prediction_labels),
        relationships=ModelRelationships(
            uploader=Links(related=url + "/users/" + str(entity.uploader)),
        ),
    )

    if entity.last_trained_on != None:
        data.relationships.last_trained_on = Links(
            related=url + "/datasets/" + str(entity.last_trained_on)
        )

    return data

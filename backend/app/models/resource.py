from ..public.api import (
    ModelAttributes,
    ModelData,
    ModelMeta,
    ModelRelationships,
    Links,
)
from .model import Model


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
        meta=ModelMeta(
            current_prediction_labels=entity.current_prediction_labels,
            param_count=entity.param_count,
        ),
        relationships=ModelRelationships(
            belongs_to=Links(related=url + "/users/" + str(entity.belongs_to)),
        ),
    )

    if entity.last_trained_on != None:
        data.relationships.last_trained_on = Links(
            related=url + "/datasets/" + str(entity.last_trained_on)
        )

    return data

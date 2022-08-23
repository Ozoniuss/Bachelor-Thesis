from ..public.api.dataset import DatasetData, DatasetAttributes
from .model import Dataset

from ..public.api import Links


def from_db_entity(url: str, entity: Dataset):

    return DatasetData(
        id=entity.id,
        attributes=DatasetAttributes(
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            labels=entity.labels,
        ),
        links=Links(self=url + "/datasets/" + str(entity.id)),
    )

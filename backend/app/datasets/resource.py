"""
Contains the resource model
"""

from dataclasses import dataclass
from typing import Union
import uuid
from .model import Dataset


@dataclass
class Links:
    self: Union[str, None] = None
    related: Union[str, None] = None


@dataclass
class DatasetAttributes:
    name: str
    description: str
    labels: list[str]
    created_at: str


@dataclass
class DatasetData:
    id: uuid.UUID
    attributes: DatasetAttributes
    links: Links
    type: str = "dataset"


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

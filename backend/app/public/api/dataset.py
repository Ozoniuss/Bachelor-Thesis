"""
Contains the resource model
"""

from dataclasses import dataclass
from typing import Union
import uuid


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

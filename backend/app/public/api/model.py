"""
Models the model resource and the api interaction.
"""

from dataclasses import dataclass
from typing import Union
import uuid
from werkzeug.datastructures import FileStorage

from .common import Links


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
    belongs_to: Links
    last_trained_on: Union[Links, None] = None


@dataclass
class ModelData:
    id: uuid.UUID
    attributes: ModelAttributes
    meta: ModelMeta
    links: Links
    relationships: ModelRelationships
    type: str = "model"


@dataclass
class ModelFilters:
    name: Union[str, None]
    public: Union[bool, None]


@dataclass
class ModelMutableData:
    name: Union[str, None]
    description: Union[str, None]
    public: Union[bool, None]

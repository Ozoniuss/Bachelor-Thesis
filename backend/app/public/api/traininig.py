"""
Models the training resource and the api interaction.
"""

from dataclasses import dataclass
from typing import Union
import uuid

from .common import Links


@dataclass
class TrainingAttributes:
    epochs: int
    accuracy: list[float]
    loss: list[float]
    val_accuracy: Union[list[float], None]
    val_loss: Union[list[float], None]
    notes: Union[str, None]
    created_at: str


@dataclass
class TrainingRelationships:
    model: Links
    dataset: Links


@dataclass
class TrainingData:
    id: uuid.UUID
    attributes: TrainingAttributes
    links: Links
    relationships: TrainingRelationships
    type: str = "training"

"""
Models the training resource and the api interaction.
"""

from dataclasses import dataclass
import uuid

from .common import Links


@dataclass
class TrainingAttributes:
    epochs: int
    accuracy: list[float]
    loss: list[float]
    val_accuracy: list[float]
    val_loss: list[float]
    notes: str
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

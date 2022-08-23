from ..public.api.traininig import (
    TrainingAttributes,
    TrainingData,
    TrainingRelationships,
)
from ..public.api import Links
from .model import Training


def from_db_entity(url: str, entity: Training):

    data = TrainingData(
        id=entity.id,
        attributes=TrainingAttributes(
            epochs=entity.epochs,
            accuracy=entity.accuracy,
            loss=entity.loss,
            val_accuracy=entity.val_accuracy,
            val_loss=entity.val_loss,
            notes=entity.notes,
            created_at=entity.created_at,
        ),
        links=Links(self=f"{url}/models/{entity.model}/trainings/{entity.id}"),
        relationships=TrainingRelationships(
            model=Links(related=f"{url}/models/{entity.model}"),
            dataset=Links(related=f"{url}/datasets/{entity.dataset}"),
        ),
    )

    return data

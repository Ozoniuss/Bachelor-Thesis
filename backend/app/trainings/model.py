from sqlalchemy import Column, ForeignKey

from sqlalchemy.dialects.postgresql import UUID, TEXT, TIMESTAMP, INTEGER, ARRAY, FLOAT
from sqlalchemy import inspect
from app.extensions import db

from sqlalchemy.schema import FetchedValue


class Training(db.Model):
    """Model for the trainings table"""

    __tablename__ = "trainings"

    id = Column(UUID, primary_key=True, server_default=FetchedValue())
    model = Column(UUID, ForeignKey("models.id"), nullable=False)
    dataset = Column(UUID, ForeignKey("datasets.id"), nullable=False)
    epochs = Column(INTEGER, nullable=False)
    accuracy = Column(ARRAY(FLOAT), nullable=False)
    loss = Column(ARRAY(FLOAT), nullable=False)
    val_accuracy = Column(ARRAY(FLOAT), nullable=True)
    val_loss = Column(ARRAY(FLOAT), nullable=True)
    notes = Column(TEXT, nullable=True)
    created_at = Column(TIMESTAMP, nullable=True)

    def __init__(
        self,
        model,
        dataset,
        epochs,
        accuracy,
        loss,
        val_accuracy=None,
        val_loss=None,
        id=None,
        created_at=None,
    ) -> None:
        super().__init__()
        self.id = id
        self.model = model
        self.dataset = dataset
        self.epochs = epochs
        self.accuracy = accuracy
        self.loss = loss
        self.val_accuracy = val_accuracy
        self.val_loss = val_loss
        self.created_at = created_at

    def __repr__(self) -> str:
        return f"<Training {self.model, self.dataset}>"

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

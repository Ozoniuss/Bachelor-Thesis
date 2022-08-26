from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import (
    UUID,
    TEXT,
    TIMESTAMP,
    BOOLEAN,
    ARRAY,
    INTEGER,
)
from sqlalchemy import inspect
from sqlalchemy.schema import FetchedValue
from app.extensions import db
from ..utils.sqlalchemy import as_dict
from sqlalchemy.sql import func


class Model(db.Model):
    """Model for the models table"""

    __tablename__ = "models"

    id = Column(UUID, primary_key=True, server_default=FetchedValue())
    name = Column(TEXT, nullable=False)
    belongs_to = Column(UUID, ForeignKey("users.id"))
    description = Column(TEXT)
    created_at = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())
    public = Column(BOOLEAN)
    last_trained_on = Column(UUID, ForeignKey("datasets.id"), nullable=True)
    current_prediction_labels = Column(ARRAY(TEXT), nullable=False)
    param_count = Column(INTEGER, nullable=False)
    trainings = db.relationship("Training", backref="model_model", lazy=True)

    def __init__(
        self,
        name,
        belongs_to,
        description,
        public,
        current_prediction_labels,
        param_count,
        last_trained_on=None,
        created_at=None,
        updated_at=None,
        id=None,
    ) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.belongs_to = belongs_to
        self.description = description
        self.last_trained_on = last_trained_on
        self.created_at = created_at
        self.updated_at = updated_at
        self.public = public
        self.current_prediction_labels = current_prediction_labels
        self.param_count = param_count

    def __repr__(self) -> str:
        return f"<Model {self.name}>"

    def as_dict(self):
        return as_dict(self)


def get_id(m: Model) -> str:
    return str(m.id)

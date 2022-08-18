from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TEXT, TIMESTAMP, BOOLEAN, ARRAY
from sqlalchemy import inspect
from sqlalchemy.schema import FetchedValue
from app.extensions import db


class Model(db.Model):
    """Model for the models table"""

    __tablename__ = "models"

    id = Column(UUID, primary_key=True, server_default=FetchedValue())
    name = Column(TEXT, nullable=False)
    uploader = Column(UUID, ForeignKey("users.id"))
    location = Column(TEXT, nullable=False)
    description = Column(TEXT)
    created_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    public = Column(BOOLEAN)
    last_trained_on = Column(UUID, ForeignKey("datasets.id"), nullable=True)
    current_prediction_labels = Column(ARRAY(TEXT), nullable=False)
    trainings = db.relationship("Training", backref="dataset", lazy=True)

    def __init__(
        self,
        name,
        uploader,
        location,
        description,
        public,
        current_prediction_labels,
        last_trained_on=None,
        created_at=None,
        updated_at=None,
        id=None,
    ) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.uploader = uploader
        self.location = location
        self.description = description
        self.last_trained_on = last_trained_on
        self.created_at = created_at
        self.updated_at = updated_at
        self.public = public
        self.current_prediction_labels = current_prediction_labels

    def __repr__(self) -> str:
        return f"<Model {self.name}>"

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

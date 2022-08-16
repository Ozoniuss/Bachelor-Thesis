from app.extensions import db
from sqlalchemy import inspect, Column
from sqlalchemy.dialects.postgresql import UUID, TEXT, TIMESTAMP, ARRAY

from sqlalchemy.schema import FetchedValue


class Dataset(db.Model):
    """Model for the datasets table"""

    __tablename__ = "datasets"

    id = Column(UUID, primary_key=True, server_default=FetchedValue())
    name = Column(TEXT, nullable=False)
    location = Column(TEXT, unique=True, nullable=False)
    description = Column(TEXT)
    labels = Column(ARRAY(TEXT), nullable=False)
    created_at = Column(TIMESTAMP, nullable=True)

    def __init__(
        self, name, location, description, labels, id=None, created_at=None
    ) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.location = location
        self.description = description
        self.labels = labels
        self.created_at = created_at

    def __repr__(self) -> str:
        return f"<Dataset {self.name}>"

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
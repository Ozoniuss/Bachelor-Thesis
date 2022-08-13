from sqlalchemy import Column, ForeignKey

from sqlalchemy.dialects.postgresql import UUID, TEXT, TIMESTAMP, BOOLEAN
from sqlalchemy import inspect
from app.extensions import db


class Model(db.Model):
    """Model for the users table"""

    __tablename__ = "models"

    id = Column(UUID, primary_key=True)
    name = Column(TEXT, nullable=False)
    uploader = Column(UUID, ForeignKey("users.id"))
    location = Column(TEXT, nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    public = Column(BOOLEAN)

    def __init__(self, id, name, location, created_at, updated_at, public) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.location = location
        self.created_at = created_at
        self.updated_at = updated_at
        self.public = public

    def __repr__(self) -> str:
        return f"<Model {self.name}>"

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

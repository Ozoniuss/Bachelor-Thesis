from sqlalchemy import Column

from sqlalchemy.dialects.postgresql import UUID, TEXT, TIMESTAMP
from sqlalchemy import inspect
from app.extensions import db

from sqlalchemy.schema import FetchedValue


class User(db.Model):
    """Model for the users table"""

    __tablename__ = "users"

    id = Column(UUID, primary_key=True, server_default=FetchedValue())
    username = Column(TEXT, unique=True, nullable=False)
    password = Column(TEXT, nullable=False)
    email = Column(TEXT, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=FetchedValue())
    models = db.relationship("Model", backref="models_belongs_to", lazy=True)

    def __init__(
        self, username, password, email, id=None, created_at=None, updated_at=None
    ) -> None:
        super().__init__()
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

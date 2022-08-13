from sqlalchemy import Column

from sqlalchemy.dialects.postgresql import UUID, TEXT, TIMESTAMP
from sqlalchemy import inspect
from app.extensions import db


class User(db.Model):
    """Model for the users table"""

    __tablename__ = "users"

    id = Column(UUID, primary_key=True)
    username = Column(TEXT, unique=True, nullable=False)
    password = Column(TEXT, nullable=False)
    email = Column(TEXT, unique=True, nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    models = db.relationship("Model", backref="author", lazy=True)

    def __init__(self, id, username, password, email, created_at, updated_at) -> None:
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

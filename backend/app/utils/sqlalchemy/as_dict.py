from app.extensions import db
from sqlalchemy import inspect


def as_dict(model: db.Model):
    return {c.key: getattr(model, c.key) for c in inspect(model).mapper.column_attrs}

from email.policy import default

import sqlalchemy
from .db_session import SqlAlchemyBase


class Users(SqlAlchemyBase):
    __tablename__ = 'users'

    ADMIN = 1
    USER = 2

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True)
    role = sqlalchemy.Column(sqlalchemy.Integer, default=USER)

import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class Users(SqlAlchemyBase):
    __tablename__ = 'users'

    ADMIN = 1
    USER = 2

    HAVE_ACCESS = 1
    DONT_HAVE_ACCESS = 0

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True)
    role = sqlalchemy.Column(sqlalchemy.Integer, default=USER)
    access = sqlalchemy.Column(sqlalchemy.Integer, default=DONT_HAVE_ACCESS)

    scripts = relationship("Scripts", back_populates="user")

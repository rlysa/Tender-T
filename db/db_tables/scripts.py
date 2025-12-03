import sqlalchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class Scripts(SqlAlchemyBase):
    __tablename__ = 'scripts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.VARCHAR(255))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('users.id'))

    user = relationship("Users", back_populates="scripts")
    files = relationship("Files", back_populates="script")

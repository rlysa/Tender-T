import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Files(SqlAlchemyBase):
    __tablename__ = 'files'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    path = sqlalchemy.Column(sqlalchemy.VARCHAR(255))
    name = sqlalchemy.Column(sqlalchemy.VARCHAR(255))
    script_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('scripts.id'))

    script = relationship("Scripts", back_populates="files")

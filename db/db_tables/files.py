import sqlalchemy
from .db_session import SqlAlchemyBase


class Files(SqlAlchemyBase):
    __tablename__ = 'files'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.VARCHAR)
    path = sqlalchemy.Column(sqlalchemy.VARCHAR)
    script_id = sqlalchemy.Column(sqlalchemy.Integer, foreign_keys=True)

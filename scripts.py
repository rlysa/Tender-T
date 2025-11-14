import sqlalchemy
from db.db_tables.db_session import SqlAlchemyBase


class Scripts(SqlAlchemyBase):
    __tablename__ = 'scripts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.VARCHAR)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)

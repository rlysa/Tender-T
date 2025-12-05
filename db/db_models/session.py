import sqlalchemy
import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as dec
from config import DB_NAME


SqlAlchemyBase = dec.declarative_base()


def init_db():
    connection_str = f'sqlite:///{DB_NAME.strip()}?check_same_thread=False'

    engine = sqlalchemy.create_engine(connection_str, echo=False)
    session_local = orm.sessionmaker(bind=engine)

    from .models import Users, Scripts, Categories, Keywords, Products, Cards, Lots
    SqlAlchemyBase.metadata.create_all(engine)

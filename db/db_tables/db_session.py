import sqlalchemy
import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as dec


SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory
    if __factory:
        return

    if not db_file.strip():
        return

    connection_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'

    engine = sqlalchemy.create_engine(connection_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_tables

    SqlAlchemyBase.metadata.create_all(engine)


def create_session():
    global __factory
    return __factory

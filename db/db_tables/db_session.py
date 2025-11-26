import sqlalchemy
from sqlalchemy import exc
import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()
__factory = None


def global_init(db_file):
    global __factory
    if __factory:
        return

    connection_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'

    try:
        engine = sqlalchemy.create_engine(connection_str, echo=False)
        __factory = orm.sessionmaker(bind=engine)

        try:
            from . import __all_tables  # Импорт всех моделей
            SqlAlchemyBase.metadata.create_all(engine)
        except ImportError as e:
            raise Exception(f'Ошибка импорта моделей таблиц: {str(e)}')

        SqlAlchemyBase.metadata.create_all(engine)
    except sqlalchemy.exc.OperationalError as e:
        raise Exception(f'Ошибка подключения к БД: {str(e)}')
    except ImportError as e:
        raise Exception(f'Ошибка импорта моделей таблиц: {str(e)}')
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise Exception(f'Ошибка SQLAlchemy: {str(e)}')
    except Exception as e:
        raise Exception(f'Неизвестная ошибка инициализации БД: {str(e)}')


def create_session():
    global __factory
    if not __factory:
        raise Exception('База данных не инициализирована. Сначала вызовите global_init()')

    try:
        return __factory
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise Exception(f'Ошибка создания сессии БД: {str(e)}')

import sqlalchemy
import sqlalchemy.orm

import database.sqlalchemy_declarative as data_objects


_session = None


def create_database(path):
    engine = sqlalchemy.create_engine('sqlite:///{}'.format(path))
    data_objects.Base.metadata.create_all(engine)


def get_database(path):
    if _session is None:
        engine = sqlalchemy.create_engine('sqlite:///{}'.format(path))
        data_objects.Base.metadata.bind = engine
        DBSession = sqlalchemy.orm.sessionmaker(bind=engine)
        global _session
        _session = DBSession()
    return _session

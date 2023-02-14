import logging
from typing import Union

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.exc import SQLAlchemyError, DBAPIError


class ORMDatabase:
    """
    Database Object is for provide DB connector based on SQLAlchemy.
    """
    engine: Engine
    session_factory: sessionmaker

    def __init__(self,
                 dialect_name: str,
                 user: str,
                 password: str,
                 host: str,
                 port: int,
                 db_name: str,
                 driver_name: Union[str, None] = None,
                 **kwargs):
        """
        Look for
        https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.create_engine.params.url

        :param dialect_name: Name of the database system. not like db_name! (ex: oracle, postgresql, mysql...)
        :param driver_name: Name of db driver module (ex: oracledb, psycopg2, pymysql, ...)
        :param user: user name in database
        :param password: Password of user
        :param host: address to access database
        :param port: port number to access database
        :param db_name: Name of database models (service name in oracle)
        :param kwargs: follow argument in sqlalchemy.create_engine()
        """
        if driver_name is None:
            prefix = f"{dialect_name}"
        else:
            prefix = f"{dialect_name}+{driver_name}"
        db_conn_url = f'{prefix}://{user}:{password}@{host}:{port}/{db_name}'
        self.engine = create_engine(db_conn_url,
                                    future=True,
                                    pool_pre_ping=True,
                                    **kwargs
                                    )
        self.session_factory = sessionmaker(self.engine, autocommit=False, future=True)

    def close(self):
        self.engine.dispose()

    def get_db_connection(self) -> Connection:
        """
        DB connection for raw SQL.
        Must be call close() or use 'with'.
        """
        conn = self.engine.connect()
        # not use get_isolation_level() - DB Privilege(roll) problems may occured by user.
        if conn.default_isolation_level != 'READ COMMITTED':
            conn.execution_options(isolation_level="READ COMMITTED")
        return conn

    def get_db_session(self) -> Session:
        """
        DB connection for ORM.
        Must be call close().
        """
        return self.session_factory()

    def get_scoped_session(self) -> scoped_session:
        """
        DB connection for ORM.
        Must be call close().
        it's create session use this method - sqlalchemy.orm.scoped_session()
        """
        return scoped_session(self.session_factory)

    def do_transaction_use_sql(self, *queries: str) -> bool:
        try:
            with self.get_db_connection() as conn:
                with conn.begin():
                    for query in queries:
                        conn.execute(text(query))
        except (SQLAlchemyError, DBAPIError) as db_e:
            logging.exception(db_e)
            return False
        except Exception as e:
            logging.exception(e)
            return False
        else:
            return True

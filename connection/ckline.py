import logging
import sys
import oracledb

from sshtunnel import BaseSSHTunnelForwarderError

from config import server_config
from core.db_engine import ORMDatabase
from core.ssh import SSHConnector


oracledb.version = "8.3.0"
sys.modules["cx_Oracle"] = oracledb

_ssh_connector: SSHConnector | None = None
_ckline_db: ORMDatabase | None = None


def get_ssh() -> SSHConnector:
    global _ssh_connector
    if _ssh_connector is None:
        raise Exception("SSH Connector instance is None.")
    return _ssh_connector


def get_ckline_db_engine() -> ORMDatabase:
    global _ckline_db
    if _ckline_db is None:
        raise Exception("DBEngine instance is None.")
    return _ckline_db


def _ssh_connect_ckline() -> bool:
    global _ssh_connector
    if _ssh_connector is None:
        _ssh_connector = SSHConnector()

    if _ssh_connector.is_connect():
        return True

    ssh_config = server_config['SSH']
    access_config = server_config['DB.CKLINE.ACCESS']
    ssh_connected = _ssh_connector.start_connect(
        ssh_host=ssh_config['Host'],
        ssh_port=ssh_config.getint('Port'),
        ssh_id=ssh_config['ID'],
        ssh_pw=ssh_config['Password'],
        remote_host_in_ssh=access_config['Host'],
        remote_port_in_ssh=access_config.getint('Port')
    )
    return ssh_connected


def connect_db() -> bool:
    try:
        global _ckline_db
        if server_config.getboolean('DEFAULT', 'SSH'):
            ssh_connected = _ssh_connect_ckline()
            if not ssh_connected:
                raise BaseSSHTunnelForwarderError("Cannot connect ssh. Check ssh value from config/config.ini.")
            host = '127.0.0.1'
            port = _ssh_connector.get_connector().local_bind_port
        else:
            host = server_config['DB.CKLINE.ACCESS']['Host']
            port = server_config.getint('DB.CKLINE.ACCESS', 'Port')

        _ckline_db = ORMDatabase(
            dialect_name='oracle',
            driver_name='cx_oracle',
            host=host,
            port=port,
            user=server_config['DB.CKLINE.ACCESS']['ID'],
            password=server_config['DB.CKLINE.ACCESS']['Password'],
            db_name=server_config['DB.CKLINE.ACCESS']['DBName'],
            pool_size=server_config['DB.CKLINE.SETTING'].getint('PoolSize'),
            max_overflow=server_config['DB.CKLINE.SETTING'].getint('MaxOverflow'),
            pool_recycle=server_config['DB.CKLINE.SETTING'].getint('PoolRecycle'),
            arraysize=server_config['DB.CKLINE.SETTING'].getint('ArraySize'),
        )
        return True
    except Exception as e:
        logging.exception(e)
        return False

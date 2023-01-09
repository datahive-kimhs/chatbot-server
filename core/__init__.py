import oracledb
from sshtunnel import BaseSSHTunnelForwarderError

from config import server_config
from core.database import ORMDatabase
from core.ssh import SSHConnector, ssh_connect_ckline


ssh = SSHConnector()

if server_config.getboolean('DEFAULT', 'SSH'):
    if not ssh.is_connect():
        ssh_connected = ssh_connect_ckline(ssh)
        if not ssh_connected:
            raise Exception("Cannot connect SSH.")
        if ssh.get_connector() is None \
                or not ssh.is_connect():
            raise BaseSSHTunnelForwarderError("SSHTunnel Not Connected!")
    _host = '127.0.0.1'
    _port = ssh.get_connector().local_bind_port
else:
    _host = server_config['DB.CKLINE.ACCESS']['Host']
    _port = server_config.getint('DB.CKLINE.ACCESS', 'Port')


"""
It's temporary code - enable support for oracledb driver.
sqlalchemy not supported oracledb in ver 1.4, but supported in ver 2.0.

22.12.19~ currently using sqlalchemy version == 1.4.45
if use ver 2.0, remove this, and can use driver name.

refference :
https://levelup.gitconnected.com/using-python-oracledb-1-0-with-sqlalchemy-pandas-django-and-flask-5d84e910cb19
"""
import sys
oracledb.version = "8.3.0"
sys.modules["cx_Oracle"] = oracledb

ckline_db = ORMDatabase(
    dialect_name='oracle',
    driver_name='cx_oracle',
    host=_host,
    port=_port,
    user=server_config['DB.CKLINE.ACCESS']['ID'],
    password=server_config['DB.CKLINE.ACCESS']['Password'],
    db_name=server_config['DB.CKLINE.ACCESS']['DBName'],
    pool_size=server_config['DB.CKLINE.SETTING'].getint('PoolSize'),
    max_overflow=server_config['DB.CKLINE.SETTING'].getint('MaxOverflow'),
    pool_recycle=server_config['DB.CKLINE.SETTING'].getint('PoolRecycle'),
)

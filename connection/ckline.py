from config import server_config
from core.database import ORMDatabase
from core.ssh import SSHConnector


def ssh_connect_ckline() -> bool:
    global sshtunneler
    ssh_connector = sshtunneler.get_connector()
    if ssh_connector is not None and ssh_connector.is_alive:
        return True

    ssh_config = server_config['SSH']
    access_config = server_config['DB.CKLINE.ACCESS']
    ssh_connected = sshtunneler.start_connect(
        ssh_host=ssh_config['Host'],
        ssh_port=ssh_config.getint('Port'),
        ssh_id=ssh_config['ID'],
        ssh_pw=ssh_config['Password'],
        remote_host_in_ssh=access_config['Host'],
        remote_port_in_ssh=access_config.getint('Port')
    )
    return ssh_connected


sshtunneler = SSHConnector()
ckline_db = ORMDatabase()

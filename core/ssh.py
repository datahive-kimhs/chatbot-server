from typing import Union

import sshtunnel
from sshtunnel import BaseSSHTunnelForwarderError

from config import server_config


class SSHConnector:
    connector: Union[sshtunnel.SSHTunnelForwarder, None]

    def __init__(self):
        self.connector = None

    def start_connect(self,
                      ssh_host: str,
                      ssh_port: int,
                      ssh_id: str,
                      ssh_pw: str,
                      remote_host_in_ssh: str,
                      remote_port_in_ssh: int) -> bool:
        """ Start ssh tunneling.
            example
                me -> ssh_host/port -> remote_host_in_ssh/port
        :param ssh_host: ssh access address
        :param ssh_port: ssh port
        :param ssh_id: ssh username == id
        :param ssh_pw: ssh password
        :param remote_host_in_ssh: access remote address in ssh
        :param remote_port_in_ssh: access remote port in ssh
        :return: True == connected / False == not connected.
        """
        if self.connector is not None and self.connector.is_alive:
            return True

        self.connector = sshtunnel.SSHTunnelForwarder(
            ssh_address_or_host=ssh_host,
            ssh_port=ssh_port,
            ssh_username=ssh_id,
            ssh_password=ssh_pw,
            remote_bind_address=(remote_host_in_ssh, remote_port_in_ssh),
        )
        self.connector.start()
        if not self.connector.is_alive:
            reason = "Not connected ssh. check ssh status - "
            reason += f"{ssh_host}:{ssh_port}"
            raise BaseSSHTunnelForwarderError(reason)
        return self.connector.is_alive

    def stop_connect(self, force: bool = False):
        if self.connector is not None:
            self.connector.stop(force=force)

    def is_connect(self) -> bool:
        if self.connector is None:
            return False
        return self.connector.is_alive

    def get_connector(self) -> sshtunnel.SSHTunnelForwarder:
        return self.connector


def ssh_connect_ckline(sshtunneler: SSHConnector) -> bool:
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

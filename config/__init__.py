import configparser

server_config = configparser.ConfigParser()
server_config.optionxform = str
server_config.read(r'./config/config.ini')

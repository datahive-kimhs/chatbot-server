import multiprocessing
import configparser


server_config = configparser.ConfigParser()
server_config.read('./config/config.ini')

wsgi_app = 'app:app'
bind = server_config['SERVER']['HOST'] + f':{server_config.getint("SERVER", "Port")}'
backlog = 2048

daemon = True

loglevel = 'info'
logconfig = './config/log_config.conf'

workers = multiprocessing.cpu_count() * 2
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 1000
timeout = 30
keepalive = 2

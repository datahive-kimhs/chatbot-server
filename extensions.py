from connection import connect_db as connect_db_to_ckline
from data.data import ModelDataExample


model_data = ModelDataExample()


def initialize():
    connected = connect_db_to_ckline()
    if not connected:
        raise Exception("Cannot Connect to CKLINE! Check server status or value of config/config.ini.")

    model_data.load_data(f'data/chatting_ckline.json', f'data/chatting_kr.json', f'data/merge_data_ja.json')
    model_data.dataset_bm25()
    # model_data.load_model()

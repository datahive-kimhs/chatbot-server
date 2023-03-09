from data.data import ModelDataExample


model_data = ModelDataExample()


def initialize():
    model_data.load_data(f'data/chatting_ckline.json', f'data/chatting_kr.json', f'data/merge_data_ja.json')
    model_data.dataset_bm25()
    model_data.load_model()

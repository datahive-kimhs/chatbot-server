import pandas as pd
from konlpy.tag import Komoran
from rank_bm25 import BM25Okapi
from utils.Preprocess import Preprocess_ja

komoran = Komoran()

p_ja = Preprocess_ja(word2index_dic='train_tools/dict/chatbot_dict_ja.bin',
                     userdic=None)

def load_corpus(dataset, lang):
    if lang == "ko":
        merge_dataset_corpus = dataset['Q']
        merge_dataset_tokenized_corpus = []
        for data in merge_dataset_corpus:
            pos_list = komoran.pos(data)
            result = [pos[0] for pos in pos_list]
            merge_dataset_tokenized_corpus.append(result)
        dataset_bm25 = BM25Okapi(merge_dataset_tokenized_corpus)
        return dataset_bm25
    elif lang == "ja":
        merge_dataset_corpus = dataset['Q']
        merge_dataset_tokenized_corpus = []
        for data in merge_dataset_corpus:
            pos_list = p_ja.pos(data)
            result = [pos[0] for pos in pos_list]
            merge_dataset_tokenized_corpus.append(result)

        dataset_bm25 = BM25Okapi(merge_dataset_tokenized_corpus)
        return dataset_bm25

def load_dataset():
    chatting_ckline = pd.read_json(f'chatting_ckline.json', encoding="UTF-8").dropna()
    chatting_kr = pd.read_json(f'chatting_kr.json', encoding="UTF-8").dropna()
    merge_dataset_ja = pd.read_json(f'merge_data_ja.json', encoding="UTF-8").dropna()
    
    return chatting_ckline, chatting_kr, merge_dataset_ja

def dataset_bm25():
    chatting_ckline, merge_dataset_ja = load_dataset()
    chatting_ckline_bm25 = load_corpus(chatting_ckline, "ko")
    merge_dataset_bm25_ja = load_corpus(merge_dataset_ja, "ja")

    return chatting_ckline_bm25, merge_dataset_bm25_ja

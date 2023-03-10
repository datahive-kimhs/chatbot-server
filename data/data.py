import pandas as pd
import torch
from konlpy.tag import Komoran
from rank_bm25 import BM25Okapi
from utils.Preprocess import Preprocess_ja
from transformers import AutoTokenizer
from transformers import TFGPT2LMHeadModel
from transformers import AutoModelForCausalLM

komoran = Komoran()

p_ja = Preprocess_ja(word2index_dic='./train_tools/dict/chatbot_dict_ja.bin',
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

class ModelDataExample:
    def __init__(self):
        self.chatting_ckline = None
        self.chatting_kr = None
        self.merge_dataset_ja = None
        self.chatting_ckline_bm25 = None
        self.merge_dataset_bm25_ja = None
        self.tokenizer = None
        self.model = None


    def load_data(self, path1, path2, path3):
        self.chatting_ckline = pd.read_json(path1, encoding="UTF-8").dropna()
        self.chatting_kr = pd.read_json(path2, encoding="UTF-8").dropna()
        self.merge_dataset_ja = pd.read_json(path3, encoding="UTF-8").dropna()

    def get_chatting_ckline(self):
        return self.chatting_ckline
    
    def get_chatting_kr(self):
        return self.chatting_kr
    
    def get_merge_dataset_ja(self):
        return self.merge_dataset_ja
    
    def dataset_bm25(self):
        self.chatting_ckline_bm25 = load_corpus(self.chatting_ckline, "ko")
        self.merge_dataset_bm25_ja = load_corpus(self.merge_dataset_ja, "ja")
    
    def get_chatting_ckline_bm25(self):
        return self.chatting_ckline_bm25

    def get_merge_dataset_bm25_ja(self):
        return self.merge_dataset_bm25_ja
    
    def load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
  'kakaobrain/kogpt', revision='KoGPT6B-ryan1.5b-float16',  # or float32 version: revision=KoGPT6B-ryan1.5b
  bos_token='[BOS]', eos_token='[EOS]', unk_token='[UNK]', pad_token='[PAD]', mask_token='[MASK]')
        self.model = AutoModelForCausalLM.from_pretrained(
  'kakaobrain/kogpt', revision='KoGPT6B-ryan1.5b-float16',  # or float32 version: revision=KoGPT6B-ryan1.5b
  pad_token_id=self.tokenizer.eos_token_id,
  torch_dtype='auto', low_cpu_mem_usage=True
).to(device='cuda', non_blocking=True)
        # self.tokenizer = AutoTokenizer.from_pretrained('skt/kogpt2-base-v2', bos_token='</s>', eos_token='</s>', pad_token='<pad>')
    
    def get_tokenizer(self):
        return self.tokenizer

    def get_model(self):
        return self.model
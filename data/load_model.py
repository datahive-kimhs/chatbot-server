from transformers import AutoTokenizer
from transformers import TFGPT2LMHeadModel

def load_model():
    tokenizer = AutoTokenizer.from_pretrained('skt/kogpt2-base-v2', bos_token='</s>', eos_token='</s>', pad_token='<pad>')
    kogpt_model = TFGPT2LMHeadModel.from_pretrained('cheonboy/kogpt2_small50')

    return tokenizer, kogpt_model

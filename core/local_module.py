import torch
from transformers import AutoTokenizer
from transformers import TFGPT2LMHeadModel
import tensorflow as tf

model = TFGPT2LMHeadModel.from_pretrained('cheonboy/kogpt2_small50')
tokenizer = AutoTokenizer.from_pretrained('skt/kogpt2-base-v2', bos_token='</s>', eos_token='</s>', pad_token='<pad>')

def return_answer(user_text):
    sent = '<usr>' + user_text + '<sys>'
    input_ids = [tokenizer.bos_token_id] + tokenizer.encode(sent)
    input_ids = tf.convert_to_tensor([input_ids])
    output = model.generate(input_ids, max_length=50, do_sample=True, top_k=50)
    sentence = tokenizer.decode(output[0].numpy().tolist())
    chatbot_response = sentence.split('<sys> ')[1].replace('</s>', '')
    return chatbot_response


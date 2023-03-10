import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained(
  'kakaobrain/kogpt', revision='KoGPT6B-ryan1.5b-float16',  # or float32 version: revision=KoGPT6B-ryan1.5b
  bos_token='[BOS]', eos_token='[EOS]', unk_token='[UNK]', pad_token='[PAD]', mask_token='[MASK]'
)
model = AutoModelForCausalLM.from_pretrained(
  'kakaobrain/kogpt', revision='KoGPT6B-ryan1.5b-float16',  # or float32 version: revision=KoGPT6B-ryan1.5b
  pad_token_id=tokenizer.eos_token_id,
  torch_dtype='auto', low_cpu_mem_usage=True
).to(device='cuda', non_blocking=True)
_ = model.eval()

def return_answer(query):
  prompt = f'''
Q : {query}
A :'''
  with torch.no_grad():
    tokens = tokenizer.encode(prompt, return_tensors='pt').to(device='cuda', non_blocking=True)
    gen_tokens = model.generate(tokens, do_sample=True, temperature=0.85, max_length=100)
    generated = tokenizer.batch_decode(gen_tokens)[0].split('\n')[2]

  return generated[4:]

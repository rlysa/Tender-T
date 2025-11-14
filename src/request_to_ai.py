import time
from datetime import datetime

import requests
import tiktoken

from config import *


def make_request_to_ai(prompt, text, model=MODEL):
    def count_tokens(t):
        tokens = []
        if 'qwen' in model.lower():
            try:
                from transformers import AutoTokenizer
                tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen2-72B-Instruct-GPTQ-Int8')
                tokens = tokenizer.encode(t)
            except Exception as e:
                print(f'Ошибка при подсчете токенов\n{e}')
        elif 'gpt' in model:
            enc = tiktoken.encoding_for_model(model.replace('openai/', ''))
            tokens = enc.encode(t)
        return tokens
    tokens_full_text = len(count_tokens(text))
    tokens_prompt = len(count_tokens(prompt))
    if tokens_full_text + tokens_prompt > MAX_TOKENS:
        max_tokens_text = (MAX_TOKENS - tokens_prompt)
        count = tokens_full_text // max_tokens_text + 1
        full_text = [prompt + text[i * max_tokens_text:i * max_tokens_text + MAX_TOKENS] for i in range(0, count)]
    else:
        full_text = [prompt + text]
    answer = []
    prompt_tokens, completion_tokens = 0, 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64',
        'Authorization': f'Bearer {AI_API_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        for part_of_text in full_text:
            print(part_of_text)
            data = {
                'model': model,
                'messages': [{'role': 'user', 'content': part_of_text}, ]
            }
            response = requests.post(AI_URL, headers=headers, json=data)
            while response.status_code != 200:
                time.sleep(60)
                print(f'{datetime.now()}: Переподключение')
                response = requests.post(AI_URL, headers=headers, json=data)

            answer.append(response.json()['choices'][0]['message']['content'])
            prompt_tokens += response.json()['usage']['prompt_tokens']
            completion_tokens += response.json()['usage']['completion_tokens']
            print(f'{datetime.now()}: Обработка запроса: {len(answer)}/{len(full_text)}')
            time.sleep(60)
    except Exception as e:
        print(f'Ошибка в отправке запроса модели: {response.status_code}\n{e}')
    return ['\n'.join(answer), prompt_tokens, completion_tokens]

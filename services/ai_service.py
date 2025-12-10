import time

import requests
import requests.exceptions
import tiktoken

from config import MODEL, AI_API_KEY, MAX_TOKENS, AI_URL


def make_request_to_ai(prompt, text, model=MODEL):
    def count_tokens(t):
        tokens = []
        try:
            if 'qwen' in model.lower():
                from transformers import AutoTokenizer
                tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen2-72B-Instruct-GPTQ-Int8')
                tokens = tokenizer.encode(t)

            elif 'gpt' in model:
                enc = tiktoken.encoding_for_model(model.replace('openai/', ''))
                tokens = enc.encode(t)
            return tokens
        except Exception as e:
            raise Exception(f'Ошибка подсчета токенов')
    try:
        tokens_full_text = len(count_tokens(text))
        tokens_prompt = len(count_tokens(prompt))

        if tokens_full_text + tokens_prompt > MAX_TOKENS:
            max_tokens_text = (MAX_TOKENS - tokens_prompt)
            count = tokens_full_text // max_tokens_text + 1
            full_text = [prompt + text[i * max_tokens_text:i * max_tokens_text + MAX_TOKENS] for i in range(0, count)]
        else:
            full_text = [prompt + text]

        answer_parts = []
        prompt_tokens, completion_tokens = 0, 0
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64',
            'Authorization': f'Bearer {AI_API_KEY}',
            'Content-Type': 'application/json'
        }

        for i, part_of_text in enumerate(full_text):
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    data = {
                        'model': model,
                        'messages': [{'role': 'user', 'content': part_of_text}, ]
                    }
                    response = requests.post(AI_URL, headers=headers, json=data, timeout=60)
                    if response.status_code == 200:
                        result = response.json()
                        answer_parts.append(result['choices'][0]['message']['content'])
                        prompt_tokens += result['usage']['prompt_tokens']
                        completion_tokens += result['usage']['completion_tokens']
                        break

                    elif response.status_code == 429:
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                    else:
                        if attempt == max_retries - 1:
                            raise Exception(f'Ошибка API: {response.status_code} - {response.text}: {response.text[:100]}')
                        time.sleep(5)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise Exception(f'Ошибка сети AI: {str(e)}')
                    time.sleep(5)
            if i < len(full_text) - 1:
                time.sleep(2)
        return ['\n'.join(answer_parts), prompt_tokens, completion_tokens]

    except Exception as e:
        raise Exception(f'Критическая ошибка AI: {str(e)}')

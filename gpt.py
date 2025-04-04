import requests
import json
import os
import dotenv
dotenv.load_dotenv()
tokens_str = os.getenv("GPT_TOKEN", "")
tokens = tokens_str.split(",") if tokens_str else []
token = tokens[0]


def gpt_ans(prompt):
    global cnt
    cnt += 1
    data = {
        "prompt": f"{prompt}"
    }
    headers = {
        "Authorization": f"Bearer {tokens[cnt]}"
    }
    response = requests.post(url, headers=headers, json=data)
    js = json.loads(response.text)
    cnt -= 1
    return js["outputFull"]['value']

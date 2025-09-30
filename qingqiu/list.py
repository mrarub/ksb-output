import requests
import os

def load_config_headers():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'list.txt')
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start = content.find('headers = {')
    end = content.find('}', start) + 1
    headers_code = content[start:end]
    
    local_vars = {}
    exec(headers_code, {}, local_vars)
    return local_vars['headers']

url = "https://api.yisouti.com/user/paper/list"

base_headers = load_config_headers()

headers = base_headers.copy()

data = """{"size":"20","page":"1"}"""

res = requests.post(url, headers=headers, data=data)
print(res.text)

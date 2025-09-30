import requests
import os

def load_config_headers():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'fetch.txt')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start = content.find('headers = {')
    end = content.find('}', start) + 1
    headers_code = content[start:end]
    
    local_vars = {}
    exec(headers_code, {}, local_vars)
    return local_vars['headers']

url = "https://api.yisouti.com/questions/fetch"

base_headers = load_config_headers()

headers = base_headers.copy()

def get_tiku_id_from_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
    
    try:
        if not os.path.exists(config_path):
            print(f"错误：配置文件 {config_path} 不存在")
            return None
        
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('tiku-id = '):
                return line.split('=', 1)[1].strip()
        
        print(f"错误：配置文件 {config_path} 中未找到tiku-id配置")
        return None
        
    except Exception as e:
        print(f"错误：无法读取配置文件 {config_path}。错误：{str(e)}")
        return None

paper_id = get_tiku_id_from_config()

if paper_id:
    data = f"""{{"paperid":"{paper_id}"}}"""
    res = requests.post(url, headers=headers, data=data)
    
    config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
    os.makedirs(config_dir, exist_ok=True)
    
    output_file_path = os.path.join(config_dir, 'timu-id.txt')
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(res.text)
        print(f"响应已成功保存到 {output_file_path}")
    except Exception as e:
        print(f"保存响应失败: {str(e)}")
else:
    print("无法获取tiku-id，请求已取消")

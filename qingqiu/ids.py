import requests
import os
import time
import random
import json

def load_config_headers():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'ids.txt')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start = content.find('headers = {')
    end = content.find('}', start) + 1
    headers_code = content[start:end]
    
    local_vars = {}
    exec(headers_code, {}, local_vars)
    return local_vars['headers']

def get_ids_from_file():
    try:
        file_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'timu-id.txt')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        start = content.find('"rows":[') + len('"rows":[')
        end = content.find(']', start)
        if start > len('"rows":[') - 1 and end > start:
            rows_content = content[start:end]
            ids_str = rows_content.replace('"', '')
            return json.loads('[' + ids_str + ']')
        else:
            return []
    except Exception as e:
        print(f"错误：无法从timu-id.txt获取ids - {e}")
        return []

def get_tiku_id_from_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
        
        if not os.path.exists(config_path):
            print(f"错误：配置文件 {config_path} 不存在")
            return None
        
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('tiku-id = '):
                tiku_id = line.split('=', 1)[1].strip().strip('"').strip("'")
                return tiku_id
        
        print(f"错误：配置文件 {config_path} 中未找到tiku-id配置")
        return None
        
    except Exception as e:
        print(f"错误：读取配置文件时发生异常 - {e}")
        return None

url = "https://api.yisouti.com/questions/ids"

base_headers = load_config_headers()

headers = base_headers.copy()

ids_list = get_ids_from_file()

paper_id = get_tiku_id_from_config()

output_file_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'timu-json.txt')

config_dir = os.path.dirname(output_file_path)
os.makedirs(config_dir, exist_ok=True)

if paper_id:
    print(f"成功获取tiku-id: {paper_id}")
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write('')
    
    success_count = 0
    for i, question_id in enumerate(ids_list):
        try:
            if i > 0:
                wait_time = random.uniform(0.5, 1.5)
                print(f"等待{wait_time:.2f}秒后请求下一个题目...")
                time.sleep(wait_time)
            
            # 构造请求体为 dict
            data = {
                "ids": f"[{question_id}]",
                "source": "顺序练习",
                "paperid": paper_id
            }

            # 确保 headers 有正确的 Content-Type
            headers["Content-Type"] = "application/json; charset=utf-8"

            print(f"正在处理题目ID: {question_id} ({i+1}/{len(ids_list)})")
            res = requests.post(url, headers=headers, json=data)
            
            with open(output_file_path, 'a', encoding='utf-8') as f:
                f.write(f"题目ID: {question_id}\n")
                f.write(res.text)
                f.write('\n\n')
                f.flush()
                os.fsync(f.fileno())
                
            success_count += 1
            print(f"题目ID: {question_id} 处理成功并已保存")
            
            if res.status_code == 403 or "封禁" in res.text:
                print("检测到可能被封禁，停止获取")
                break
        except Exception as e:
            print(f"处理题目ID: {question_id} 时发生错误: {str(e)}")
            continue
    
    print(f"题目请求完成，成功获取 {success_count}/{len(ids_list)} 道题目")
    print(f"结果已保存到：{output_file_path}")
else:
    print("无法获取有效的tiku-id，请求已取消")

import json
import sys
import os
def string_to_json_pretty(json_string):
    try:
        cleaned_string = json_string.replace('\/','/')
        json_obj = json.loads(cleaned_string)
        return json.dumps(json_obj, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"解析错误: {str(e)}"

def process_timu_json_file(file_path, output_file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace('<br>', '')
            
        if not content.strip():
            print("文件内容为空")
            return
            
        questions = []
        current_question = {}
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('题目ID: '):
                if current_question:
                    questions.append(current_question)
                    current_question = {}
                question_id = line[len('题目ID: '):].strip()
                current_question['id'] = question_id
            elif current_question.get('id') and not current_question.get('json'):
                current_question['json'] = line
        
        if current_question:
            questions.append(current_question)
        
        print(f"成功解析 {len(questions)} 道题目\n")
        
        output_content = ""
        
        for i, q in enumerate(questions):
            print(f"===== 题目 {i+1} (ID: {q['id']}) =====")
            result = string_to_json_pretty(q['json'])
            print(result)
            print()
            
            output_content += f"===== 题目 {i+1} (ID: {q['id']}) =====\n"
            output_content += f"{result}\n\n"
            
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
            
        print(f"所有题目解析完成，共 {len(questions)} 道题目")
        print(f"结果已保存到: {output_file_path}")
            
    except Exception as e:
        print(f"处理文件失败: {str(e)}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_file_path = os.path.join(script_dir, '..', 'config', 'timu-json.txt')
    default_output_path = os.path.join(script_dir, '..', 'config', 'json-jiexi.txt')
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if len(sys.argv) > 2:
            output_file_path = sys.argv[2]
        else:
            output_file_path = default_output_path
    else:
        file_path = default_file_path
        output_file_path = default_output_path
        print(f"未指定文件路径，使用默认路径: {file_path}")
        print(f"结果将保存到: {output_file_path}")
        
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        
        if file_path == default_file_path:
            print("请先执行导出操作生成timu-json.txt文件")
        
        print("\nJSON字符串美化工具")
        print("输入JSON字符串，输出美化格式")
        
        while True:
            print("请输入JSON字符串 (输入 'quit' 退出):")
            json_string = input().strip()
            
            if json_string.lower() == 'quit':
                print("退出程序")
                break
                
            if not json_string:
                print("请输入有效的JSON字符串")
                continue
                
            result = string_to_json_pretty(json_string)
            print("美化格式:")
            print(result)
        return
    
    process_timu_json_file(file_path, output_file_path)

if __name__ == "__main__":
    main()

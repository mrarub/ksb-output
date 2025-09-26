import json
import re
import os
import configparser
import subprocess
import argparse
import sys

class QuestionConverter:
    def __init__(self, json_file_path, output_file_path=None):
        self.json_file_path = json_file_path
        if output_file_path:
            self.output_file_path = output_file_path
        else:
            save_dir = self._get_save_directory()
            if save_dir and os.path.isdir(save_dir):
                self.output_file_path = os.path.join(save_dir, "timu.md")
            else:
                self.output_file_path = os.path.join(os.path.dirname(json_file_path), "timu.md")
        os.makedirs(os.path.dirname(self.output_file_path), exist_ok=True)
        self.qtype_map = {
            "1": "单选题",
            "2": "多选题",
            "3": "判断题",
            "4": "填空题",
            "5": "简答题",
            "11": "论述题",
            "12": "计算题",
            "14": "不定项选择题",
            "15": "排序题"
        }
        self.question_stats = {}
    
    def _get_config(self):
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.ini')
        config = configparser.ConfigParser()
        config.optionxform = str
        
        if os.path.exists(config_file):
            try:
                config.read(config_file, encoding='utf-8')
                return config
            except Exception as e:
                print(f"读取配置文件失败: {e}")
        return None
    
    def _get_save_directory(self):
        config = self._get_config()
        
        if config and config.has_option('Config', 'lujing'):
            try:
                return config.get('Config', 'lujing')
            except Exception as e:
                print(f"读取lujing配置失败: {e}")
        
        return None
    
    def process_text(self, text):
        if not text:
            return ""
        try:
            if isinstance(text, str):
                if '\\u' in text:
                    try:
                        text = text.encode('utf-8').decode('unicode_escape')
                    except:
                        pass
                def replace_img_tag(match):
                    img_tag = match.group(0)
                    src_match = re.search(r'src=[\'"]([^\'"]+)[\'"]', img_tag)                   
                    if src_match:
                        src = src_match.group(1)
                        return f"![]({src})"
                    return img_tag
                text = re.sub(r'<img[^>]+>', replace_img_tag, text)
                text = re.sub(r'<p>', '', text)
                text = re.sub(r'</p>', '', text)
            return text
        except Exception:
            return text
    
    def extract_chapters(self, chapters_data):
        """提取章节信息"""
        if not chapters_data:
            return ""
        try:
            if isinstance(chapters_data, str):
                chapters = json.loads(chapters_data)
            else:
                chapters = chapters_data
            
            if not chapters:
                return ""
            chapter_titles = [chapter['title'] for chapter in chapters if 'title' in chapter]
            return "、".join(chapter_titles)
        except Exception:
            return ""
    
    def parse_options(self, options_str):
        if not options_str:
            return []
        
        try:
            options = json.loads(options_str)
            formatted_options = []
            for option in options:
                key = option.get('Key', '')
                value = option.get('Value', '')
                clean_value = self.process_text(value)
                formatted_options.append(f"{key}. {clean_value}")
            return formatted_options
        except Exception:
            return []
    
    def _should_export_analysis(self):
        config = self._get_config()
        if config and config.has_option('Config', 'jiexi'):
            try:
                jiexi_value = config.get('Config', 'jiexi').lower()
                return jiexi_value == 'true'
            except Exception as e:
                print(f"读取jiexi配置失败: {e}")
        return True
    
    def _format_question(self, question_num, question_data, qtype, question_type):
        question_content = self.process_text(question_data.get('question', ''))
        options_str = question_data.get('options', '')
        answer = question_data.get('answer', '')
        analysis = self.process_text(question_data.get('analysis', ''))
        ai_analysis = self.process_text(question_data.get('ai_analysis', ''))
        chapters = self.extract_chapters(question_data.get('chapters', ''))
        self.question_stats[question_type] = self.question_stats.get(question_type, 0) + 1
        if qtype == '3': 
            md_question = f"{question_num}、{question_content}\n\n"
            if answer == 'A':

                md_question += f"答案：正确\n\n"
            elif answer == 'B':
                md_question += f"答案：错误\n\n"
            else:
                md_question += f"答案：{answer}\n\n"
        else: 
            md_question = f"{question_num}、{question_content}\n\n"
            options = self.parse_options(options_str)
            if options:
                md_question += "\n".join(options) + "\n\n"
            if answer:
                md_question += f"答案：{answer}\n\n"
        export_analysis = self._should_export_analysis()
        if export_analysis:
            if analysis:
                md_question += f"解析：{analysis}\n\n"
            elif ai_analysis:
                md_question += f"解析：{ai_analysis}\n\n"
        if chapters:
            md_question += f"章节：{chapters}\n"
        
        return md_question
    
    def convert_to_md(self):
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            question_blocks = re.split(r'===== 题目 \d+ \(ID: \d+\) =====', content)
            question_blocks = [block.strip() for block in question_blocks if block.strip()]
            questions_by_type = {}
            question_num = 0
            
            for block in question_blocks:
                try:
                    data = json.loads(block)
                    if data.get('code') != '200' or not data.get('data'):
                        continue
                    
                    question_data = data['data'][0]
                    question_num += 1
                    qtype = question_data.get('qtype', '')
                    question_type = self.qtype_map.get(qtype, '其他题型')
                    md_question = self._format_question(question_num, question_data, qtype, question_type)
                    if question_type not in questions_by_type:
                        questions_by_type[question_type] = []
                    questions_by_type[question_type].append(md_question)
                except Exception as e:
                    print(f"解析题目块时出错: {e}")
                    continue
            md_content = []
            for question_type, questions in questions_by_type.items():
                md_content.append(f"{question_type}\n")
                md_content.extend(questions)
                md_content.append("")
            with open(self.output_file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(md_content))
            
            print(f"转换完成！共处理 {question_num} 道题目")
            print(f"各类型题目数量：{self.question_stats}")
            print(f"Markdown文件已保存至：{self.output_file_path}")
            
        except Exception as e:
            print(f"转换过程中出错: {e}")

def convert_to_docx(md_file_path):
    docx_file_path = os.path.join(os.path.dirname(md_file_path), "timu.docx")
    try:
        subprocess.run([
            'pandoc', 
            md_file_path, 
            '-o', 
            docx_file_path
        ], check=True)
        print(f"已成功将Markdown文件转换为Word文档：{docx_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"转换为Word文档时出错: {e}")
    except Exception as e:
        print(f"执行pandoc转换时发生错误: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_input_file = os.path.join(script_dir, '..', 'config', 'json-jiexi.txt')
    
    parser = argparse.ArgumentParser(description='将JSON格式题目转换为Markdown格式')
    parser.add_argument('--input', type=str, default=default_input_file, 
                        help='输入的JSON文件路径')
    parser.add_argument('--output', type=str, default=None, 
                        help='输出的Markdown文件路径')
    
    args = parser.parse_args()
    
    converter = QuestionConverter(args.input, args.output)
    converter.convert_to_md()
    config = converter._get_config()
    if config and config.has_option('Config', 'geshi'):
        try:
            geshi_value = config.get('Config', 'geshi').lower()
            if geshi_value == 'docx':
                convert_to_docx(converter.output_file_path)
        except Exception as e:
            print(f"读取geshi配置失败: {e}")

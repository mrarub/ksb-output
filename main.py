import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
import os
import subprocess
import json
import sys
import threading


class LoginApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("ksb导出")
        self.root.resizable(True, True)
        
        self._center_window(450, 500)
        
        self._create_ui()
        
        self._real_token = ""
        
        self._load_token_from_file()
    
    def _load_token_from_file(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_dir = os.path.join(current_dir, "config")
            token_file_path = os.path.join(config_dir, "token.txt")
            
            if os.path.exists(token_file_path):
                with open(token_file_path, 'r', encoding='utf-8') as f:
                    token_content = f.read().strip()
                    
                if token_content:
                    self._real_token = token_content
                    self.token_var.set("*" * 16)
        except Exception as e:
            pass
    
    def _center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_ui(self):
        self.main_frame = ttk.Frame(self.root, padding=(20, 20, 20, 20))
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.title_label = ttk.Label(
            self.main_frame,
            text="ksb导出",
            font=("Microsoft YaHei UI", 16, "bold")
        )
        self.title_label.pack(pady=(0, 20))
        
        self.form_frame = ttk.Frame(self.main_frame, padding=(10, 10, 10, 10))
        self.form_frame.pack(fill=tk.X)
        
        self._create_token_input()
        
        self._create_save_button()
        
        self.separator = ttk.Separator(self.main_frame)
        self.separator.pack(fill=tk.X, pady=10)
        
        self._create_config_frame()
        
        self.form_frame.columnconfigure(1, weight=1)
        self.config_frame.columnconfigure(1, weight=1)
    
    def _create_token_input(self):
        self.token_var = tk.StringVar()
        
        self.token_label = ttk.Label(self.form_frame, text="Token:")
        self.token_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.token_entry = ttk.Entry(self.form_frame, textvariable=self.token_var)
        self.token_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=5)
        
        self.token_entry.bind("<FocusIn>", self._on_token_entry_focus_in)
        self.token_entry.bind("<FocusOut>", self._on_token_entry_focus_out)
    
    def _create_save_button(self):
        self.save_button = ttk.Button(
            self.form_frame,
            text="保存",
            command=self.save_token
        )
        self.save_button.grid(row=1, column=0, columnspan=2, pady=(10, 20))
    
    def _create_config_frame(self):
        self.config_frame = ttk.LabelFrame(
            self.main_frame,
            text="配置选项",
            padding=(10, 10, 10, 10)
        )
        self.config_frame.pack(fill=tk.X, pady=(0, 10))
        
        self._create_question_bank_id_input()
        
        self._create_question_banks_selector()
        
        self._create_ai_analysis_selector()
        
        self._create_output_format_selector()
        
        self._create_save_directory_selector()
        
        self._create_export_button()
    
    def _create_question_bank_id_input(self):
        self.question_bank_id_var = tk.StringVar()
        
        self.question_bank_id_label = ttk.Label(self.config_frame, text="题库ID:")
        self.question_bank_id_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.question_bank_id_entry = ttk.Entry(
            self.config_frame,
            textvariable=self.question_bank_id_var
        )
        self.question_bank_id_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=5)
    
    def _create_question_banks_selector(self):
        self.question_banks_var = tk.StringVar(value="")
        self.question_banks_data = []
        
        self.question_banks_label = ttk.Label(self.config_frame, text="我的题库:")
        self.question_banks_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.question_banks_combobox = ttk.Combobox(
            self.config_frame,
            textvariable=self.question_banks_var,
            values=[],
            state="readonly"
        )
        self.question_banks_combobox.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        self.get_question_banks_button = ttk.Button(
            self.config_frame,
            text="获取题库列表",
            command=self.get_question_banks
        )
        self.get_question_banks_button.grid(row=1, column=2, padx=(5, 0), pady=5)
        
        self.question_banks_combobox.bind("<<ComboboxSelected>>", self.on_question_bank_selected)
    
    def _create_ai_analysis_selector(self):
        self.ai_analysis_var = tk.StringVar(value="开启")
        
        self.ai_analysis_label = ttk.Label(self.config_frame, text="解析:")
        self.ai_analysis_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.ai_analysis_combobox = ttk.Combobox(
            self.config_frame,
            textvariable=self.ai_analysis_var,
            values=["开启", "关闭"],
            state="readonly"
        )
        self.ai_analysis_combobox.grid(row=2, column=1, columnspan=2, sticky=tk.EW, pady=5)
    
    def _create_output_format_selector(self):
        self.output_format_var = tk.StringVar(value="md")
        
        self.output_format_label = ttk.Label(self.config_frame, text="输出格式:")
        self.output_format_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.radio_frame = ttk.Frame(self.config_frame)
        self.radio_frame.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        formats = [
            ("markdown", "md"),
            ("word", "docx")
        ]
        
        for text, value in formats:
            radio = ttk.Radiobutton(
                self.radio_frame,
                text=text,
                variable=self.output_format_var,
                value=value
            )
            radio.pack(side=tk.LEFT, padx=10)
    
    def _create_save_directory_selector(self):
        self.save_dir_var = tk.StringVar()
        
        self.save_dir_label = ttk.Label(self.config_frame, text="保存目录:")
        self.save_dir_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.save_dir_entry = ttk.Entry(
            self.config_frame,
            textvariable=self.save_dir_var
        )
        self.save_dir_entry.grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        self.browse_button = ttk.Button(
            self.config_frame,
            text="浏览...",
            command=self.browse_directory
        )
        self.browse_button.grid(row=4, column=2, padx=(5, 0), pady=5)
    
    def _create_export_button(self):
        self.export_button = ttk.Button(
            self.config_frame,
            text="导出",
            command=self.export_config
        )
        self.export_button.grid(row=5, column=0, columnspan=3, pady=(10, 0), sticky=tk.EW)
        
    def export_config(self):
        question_bank_id = self.question_bank_id_var.get().strip()
        if not question_bank_id:
            messagebox.showwarning("警告", "请输入或选择题库ID")
            return
        
        save_directory = self.save_dir_var.get().strip()
        if not save_directory:
            messagebox.showwarning("警告", "请选择保存目录")
            return
        
        self.export_button.config(state="disabled")
        
        export_thread = threading.Thread(target=self._export_in_thread, args=(question_bank_id,))
        export_thread.daemon = True
        export_thread.start()
    
    def _export_in_thread(self, question_bank_id):
        try:
            ai_analysis = self.ai_analysis_var.get()
            jiexi = "true" if ai_analysis == "开启" else "false"
            
            save_directory = self.save_dir_var.get().strip()
            
            output_format = self.output_format_var.get()
            
            config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
            os.makedirs(config_dir, exist_ok=True)
            
            config_file_path = os.path.join(config_dir, "config.ini")
            with open(config_file_path, 'w', encoding='utf-8') as f:
                f.write("[Config]\n")
                f.write(f"tiku-id = {question_bank_id}\n")
                f.write(f"jiexi = {jiexi}\n")
                f.write(f"geshi = {output_format}\n")
                f.write(f"lujing = {save_directory}\n")
            
            try:
                python_exe = sys.executable
                current_dir = os.path.dirname(os.path.abspath(__file__))
                scripts = [
                    ("fetch.py", "正在获取题目数据..."),
                    ("ids.py", "正在处理题目ID..."),
                    ("json_to_string.py", "正在转换JSON格式..."),
                    ("daochu.py", "正在导出题目...")
                ]
                
                for script_name, message in scripts:
                    script_path = os.path.join(current_dir, "qingqiu", script_name)
                    print(message)
                    subprocess.run([python_exe, script_path], check=True, cwd=current_dir)
                
                self.root.after(0, self._export_success)
            except subprocess.CalledProcessError as e:
                self.root.after(0, self._export_error, f"导出脚本执行失败: {str(e)}")
            except Exception as e:
                self.root.after(0, self._export_error, f"执行导出脚本时发生错误: {str(e)}")
            
        except Exception as e:
            self.root.after(0, self._export_error, f"保存配置失败: {str(e)}")
    
    def _export_success(self):
        messagebox.showinfo("成功", "题目已导出完成")
        self.export_button.config(state="normal")
    
    def _export_error(self, error_message):
        messagebox.showerror("错误", error_message)
        self.export_button.config(state="normal")
    
    def save_token(self):
        token_text = self.token_var.get().strip()
        
        if not token_text:
            messagebox.showwarning("警告", "请输入token信息")
            return
        
        try:
            if token_text.startswith("*") and self._real_token:
                headers_content = self.parse_token_headers(self._real_token)
            else:
                headers_content = self.parse_token_headers(token_text)
                self._real_token = token_text
            
            if not headers_content:
                messagebox.showerror("错误", "无法解析token中的headers信息")
                return
            
            config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
            os.makedirs(config_dir, exist_ok=True)
            token_file_path = os.path.join(config_dir, "token.txt")
            with open(token_file_path, 'w', encoding='utf-8') as f:
                f.write(headers_content)
            
            self.token_var.set("*" * 16)
            messagebox.showinfo("成功", "Token信息已保存到token.txt文件")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def parse_token_headers(self, token_text):
        headers_pattern = r'headers\s*=\s*{[^}]*}'
        headers_match = re.search(headers_pattern, token_text, re.DOTALL | re.IGNORECASE)
        
        if headers_match:
            return headers_match.group(0)
        
        return None
        
    def _on_token_entry_focus_in(self, event):
        if self._real_token and self.token_var.get().startswith("*"):
            self.token_var.set(self._real_token)
            
    def _on_token_entry_focus_out(self, event):
        if self._real_token and not self.token_var.get().startswith("*"):
            self.token_var.set("*" * 16)

    def get_question_banks(self):
        try:
            self.get_question_banks_button.config(state="disabled")
            
            messagebox.showinfo("提示", "正在获取题库列表，请稍候...")
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            list_py_path = os.path.join(current_dir, "qingqiu", "list.py")
            
            result = subprocess.run(
                [sys.executable, list_py_path],
                capture_output=True,
                text=True,
                cwd=current_dir
            )
            
            if result.returncode != 0:
                messagebox.showerror("错误", f"执行list.py失败: {result.stderr}")
                return
            
            json_str = result.stdout
            
            try:
                cleaned_string = json_str.replace('\\/', '/')
                data = json.loads(cleaned_string)
            except json.JSONDecodeError as e:
                messagebox.showerror("错误", f"解析JSON失败: {str(e)}")
                return
            
            if "code" in data and data["code"] == "200" and "data" in data and "rows" in data["data"]:
                rows = data["data"]["rows"]
                
                self.question_banks_data = rows
                
                display_items = []
                for item in rows:
                    if "paperid" in item and "name" in item:
                        display_items.append(f"{item['paperid']}: {item['name']}")
                
                self.question_banks_combobox['values'] = display_items
                
                if display_items:
                    messagebox.showinfo("成功", f"成功获取{len(display_items)}个题库")
                else:
                    messagebox.showinfo("提示", "未找到题库数据")
            else:
                messagebox.showerror("错误", "返回数据格式不正确或没有找到题库列表")
                
        except Exception as e:
            messagebox.showerror("错误", f"获取题库列表失败: {str(e)}")
        finally:
            self.get_question_banks_button.config(state="normal")
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_dir_var.set(directory)
    
    def _save_directory_to_config(self, directory):
        try:
            config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
            os.makedirs(config_dir, exist_ok=True)
            
            config_file_path = os.path.join(config_dir, "config.ini")
            config_data = {}
            if os.path.exists(config_file_path):
                with open(config_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            config_data[key.strip()] = value.strip()
            
            config_data['lujing'] = directory
            
            with open(config_file_path, 'w', encoding='utf-8') as f:
                f.write("[Config]\n")
                for key, value in config_data.items():
                    f.write(f"{key} = {value}\n")
        except Exception as e:
            messagebox.showerror("错误", f"保存目录配置失败: {str(e)}")
    
    def on_question_bank_selected(self, event):
        selected_text = self.question_banks_var.get()
        
        if selected_text:
            try:
                paperid = selected_text.split(":")[0].strip()
                self.question_bank_id_var.set(paperid)
            except:
                pass


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()

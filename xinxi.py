import tkinter as tk
from tkinter import ttk, messagebox
import os
import re

class requestsInputApp:
    def __init__(self, root):
        self.root = root
        self.root.title("requests信息输入")
        self.root.resizable(False, False)
        
        self._center_window(500, 600)
        
        self._create_ui()
        
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
            text="请输入reuests信息",
            font=("Microsoft YaHei UI", 14, "bold")
        )
        self.title_label.pack(pady=(0, 20))
        self.list_frame = ttk.LabelFrame(self.main_frame, text="list", padding=(10, 10, 10, 10))
        self.list_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.list_info = ttk.Label(
            self.list_frame,
            text="请粘贴List接口的完整requests代码:",
            wraplength=500
        )
        self.list_info.pack(pady=(0, 5))
        
        self.list_text = tk.Text(self.list_frame, height=5, width=60)
        self.list_text.pack(pady=(0, 5))
        self.fetch_frame = ttk.LabelFrame(self.main_frame, text="fetch", padding=(10, 10, 10, 10))
        self.fetch_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.fetch_info = ttk.Label(
            self.fetch_frame,
            text="请粘贴Fetch接口的完整requests代码:",
            wraplength=500
        )
        self.fetch_info.pack(pady=(0, 5))
        
        self.fetch_text = tk.Text(self.fetch_frame, height=5, width=60)
        self.fetch_text.pack(pady=(0, 5))
        self.ids_frame = ttk.LabelFrame(self.main_frame, text="ids", padding=(10, 10, 10, 10))
        self.ids_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.ids_info = ttk.Label(
            self.ids_frame,
            text="请粘贴IDS接口的完整requests代码:",
            wraplength=500
        )
        self.ids_info.pack(pady=(0, 5))
        
        self.ids_text = tk.Text(self.ids_frame, height=5, width=60)
        self.ids_text.pack(pady=(0, 5))
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.save_button = ttk.Button(
            self.button_frame,
            text="保存",
            command=self.save_requestss
        )
        self.save_button.pack(side=tk.RIGHT)
        
        self.cancel_button = ttk.Button(
            self.button_frame,
            text="取消",
            command=self.root.destroy
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(0, 10))
        self._load_existing_requests()
    
    def save_requestss(self):
        list_content = self.list_text.get("1.0", tk.END).strip()
        fetch_content = self.fetch_text.get("1.0", tk.END).strip()
        ids_content = self.ids_text.get("1.0", tk.END).strip()
        if not any([list_content, fetch_content, ids_content]):
            messagebox.showwarning("警告", "请至少输入一个requests信息")
            return
        
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_dir = os.path.join(current_dir, "config")
            os.makedirs(config_dir, exist_ok=True)
            
            success_count = 0
            if list_content:
                list_headers = self.extract_headers(list_content)
                if list_headers:
                    list_file_path = os.path.join(config_dir, "list.txt")
                    with open(list_file_path, 'w', encoding='utf-8') as f:
                        f.write(list_headers)
                    success_count += 1
                else:
                    messagebox.showwarning("警告", "List requests中未找到有效的headers信息")

            if fetch_content:
                fetch_headers = self.extract_headers(fetch_content)
                if fetch_headers:
                    fetch_file_path = os.path.join(config_dir, "fetch.txt")
                    with open(fetch_file_path, 'w', encoding='utf-8') as f:
                        f.write(fetch_headers)
                    success_count += 1
                else:
                    messagebox.showwarning("警告", "Fetch requests中未找到有效的headers信息")

            if ids_content:
                ids_headers = self.extract_headers(ids_content)
                if ids_headers:
                    ids_file_path = os.path.join(config_dir, "ids.txt")
                    with open(ids_file_path, 'w', encoding='utf-8') as f:
                        f.write(ids_headers)
                    success_count += 1
                else:
                    messagebox.showwarning("警告", "IDS reuests中未找到有效的headers信息")
            
            if success_count > 0:
                messagebox.showinfo("成功", f"成功保存了{success_count}个requests文件")
                self.root.destroy()
            else:
                messagebox.showerror("错误", "没有保存任何有效的requests文件")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def extract_headers(self, requests_text):
        headers_pattern = r'headers\s*=\s*{[^}]*}'
        headers_match = re.search(headers_pattern, requests_text, re.DOTALL | re.IGNORECASE)
        
        if headers_match:
            return headers_match.group(0)
        
        return None
    
    def _load_existing_requests(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_dir = os.path.join(current_dir, "config")
            list_file_path = os.path.join(config_dir, "list.txt")
            if os.path.exists(list_file_path):
                with open(list_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.list_text.insert("1.0", content)
            fetch_file_path = os.path.join(config_dir, "fetch.txt")
            if os.path.exists(fetch_file_path):
                with open(fetch_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.fetch_text.insert("1.0", content)
            ids_file_path = os.path.join(config_dir, "ids.txt")
            if os.path.exists(ids_file_path):
                with open(ids_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.ids_text.insert("1.0", content)
        except Exception as e:
            print(f"加载现有requests时出错: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = requestsInputApp(root)
    root.mainloop()
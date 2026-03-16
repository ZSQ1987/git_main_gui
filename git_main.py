import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import subprocess
import os
import sys

class GitBashGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("快速 Git Bash 工具 - Python 3.11.9 + ttk")
        
        # 初始窗口大小（增加长宽高）
        window_width = 900
        window_height = 700
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(700, 500)    # 最小窗口大小
        
        # 计算居中位置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口位置居中
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 初始化工作目录（默认当前目录）
        self.working_dir = os.getcwd()
        
        # 主框架，用于更好的布局管理
        main_frame = ttk.Frame(self.root, padding=(10, 10, 10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. 工作目录选择区
        self.create_dir_selector(main_frame)
        
        # 2. 常用 Git 命令快捷按钮区
        self.create_quick_commands(main_frame)
        
        # 3. 自定义命令输入区
        self.create_custom_command_area(main_frame)
        
        # 4. 命令输出显示区
        self.create_output_area(main_frame)

    def create_dir_selector(self, parent):
        """创建工作目录选择区域"""
        frame = ttk.Frame(parent)
        frame.pack(padx=0, pady=5, fill=tk.X)
        
        ttk.Label(frame, text="🔍 工作目录：").pack(side=tk.LEFT, padx=5)
        self.dir_var = tk.StringVar(value=self.working_dir)
        dir_entry = ttk.Entry(frame, textvariable=self.dir_var, state="readonly")
        dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 功能说明按钮
        help_btn = ttk.Button(frame, text="功能说明", command=self.show_help)
        help_btn.pack(side=tk.RIGHT, padx=5)
        
        # 选择目录按钮
        select_btn = ttk.Button(frame, text="选择目录", command=self.select_working_dir)
        select_btn.pack(side=tk.RIGHT, padx=5)
    
    def show_help(self):
        """显示功能说明弹窗"""
        # 创建自定义消息框
        help_window = tk.Toplevel(self.root)
        help_window.title("📖 功能说明")
        help_window.geometry("600x400")
        help_window.resizable(True, True)
        
        # 居中显示
        help_window.transient(self.root)
        help_window.grab_set()
        
        # 计算居中位置
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        
        window_width = 600
        window_height = 400
        
        x = root_x + (root_width - window_width) // 2
        y = root_y + (root_height - window_height) // 2
        
        help_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 添加功能说明文本
        description_text = """
        【核心功能】
        1. 常用 Git 命令快捷按钮：点击按钮可将命令填充到输入框，方便快速执行；
        2. 自定义命令输入：支持手动输入任意 Git 命令（如 git log、git branch 等）；
        3. 工作目录选择：可切换 Git 命令的执行目录（默认当前目录）；
        4. 实时输出显示：执行命令后，结果/错误信息会实时显示在下方输出区；
        5. 清空输出：一键清空输出区内容，方便查看新的执行结果。
        
        【使用提示】
        - 执行命令前请确保已安装 Git，并配置好环境变量；
        - 执行 git commit 时需手动补充提交信息（如 git commit -m "更新内容"）；
        - 输出区红色文字为错误信息，黑色为正常执行结果。
        """
        
        # 创建文本框显示说明
        text_frame = ttk.Frame(help_window)
        text_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        text = scrolledtext.ScrolledText(text_frame, font=("SimHei", 10), wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, description_text)
        text.config(state=tk.DISABLED)
        
        # 添加关闭按钮
        btn_frame = ttk.Frame(help_window)
        btn_frame.pack(padx=20, pady=10, fill=tk.X)
        
        close_btn = ttk.Button(btn_frame, text="关闭", command=help_window.destroy, style="Accent.TButton")
        close_btn.pack(side=tk.RIGHT, padx=5)


    def select_working_dir(self):
        """选择Git命令执行的工作目录"""
        selected_dir = filedialog.askdirectory(title="选择Git工作目录", initialdir=self.working_dir)
        if selected_dir:
            self.working_dir = selected_dir
            self.dir_var.set(selected_dir)
            self.append_output(f"✅ 已切换工作目录：{self.working_dir}", is_error=False)

    def create_quick_commands(self, parent):
        """创建常用Git命令快捷按钮区域"""
        
        # 创建命令区域
        create_frame = ttk.LabelFrame(parent, text="📁 创建相关命令")
        create_frame.pack(padx=0, pady=5, fill=tk.X)
        
        # 定义创建相关命令（按钮文本: 命令内容）
        create_commands = {
            "初始化仓库 (git init)": "git init",
            "克隆仓库 (git clone)": "git clone ",
            "创建分支 (git checkout -b)": "git checkout -b new_branch",
            "添加远程仓库 (git remote add)": "git remote add origin ",
            "创建README.md": "echo '# Project Title\n\nDescription of the project.' > README.md",
            "创建Python .gitignore": "echo '# Python\n__pycache__/\n*.py[cod]\n*$py.class\n\n# Environment\n.env\n.venv\nvenv/\nenv/\n\n# IDE\n.vscode/\n.idea/\n*.swp\n*.swo\n*~\n\n# OS\n.DS_Store\nThumbs.db' > .gitignore",
            "创建MIT License": "echo '# MIT License\n\nCopyright (c) [year] [fullname]\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the \"Software\"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.' > LICENSE"
        }
        
        # 排版创建命令按钮（每行3个）
        row, col = 0, 0
        for btn_text, cmd in create_commands.items():
            btn = ttk.Button(create_frame, text=btn_text, 
                             command=lambda c=cmd: self.fill_command(c))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky=tk.W+tk.E)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # 让列自适应宽度
        for i in range(3):
            create_frame.grid_columnconfigure(i, weight=1)
        
        # 更新命令区域
        update_frame = ttk.LabelFrame(parent, text="🔄 更新相关命令")
        update_frame.pack(padx=0, pady=5, fill=tk.X)
        
        # 定义更新相关命令（按钮文本: 命令内容）
        update_commands = {
            "查看状态 (git status)": "git status",
            "添加所有文件 (git add .)": "git add .",
            "提交（需补信息）": "git commit -m \"\"",
            "推送到远程 (git push)": "git push",
            "拉取远程代码 (git pull)": "git pull",
            "查看分支 (git branch)": "git branch",
            "切换分支 (git checkout)": "git checkout main",
            "查看远程仓库 (git remote -v)": "git remote -v",
            "首次推送 (git push -u)": "git push -u origin main",
            "上传main分支": "git push origin main"
        }
        
        # 排版更新命令按钮（每行3个）
        row, col = 0, 0
        for btn_text, cmd in update_commands.items():
            btn = ttk.Button(update_frame, text=btn_text, 
                             command=lambda c=cmd: self.fill_command(c))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky=tk.W+tk.E)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # 让列自适应宽度
        for i in range(3):
            update_frame.grid_columnconfigure(i, weight=1)

    def fill_command(self, command):
        """将快捷命令填充到自定义输入框"""
        self.cmd_text.delete(1.0, tk.END)
        self.cmd_text.insert(tk.END, command)
        # 若为commit命令，将光标定位到引号中间
        if "git commit -m \"\"" in command:
            self.cmd_text.focus()
            self.cmd_text.icursor(len("git commit -m \"") )

    def create_custom_command_area(self, parent):
        """创建自定义命令输入和执行区域"""
        frame = ttk.LabelFrame(parent, text="✏️ 自定义 Git 命令")
        frame.pack(padx=0, pady=5, fill=tk.X)
        
        # 命令输入框（多行）
        self.cmd_text = tk.Text(frame, font=("Consolas", 10), height=4, wrap=tk.WORD)
        self.cmd_text.pack(padx=5, pady=5, fill=tk.X, expand=True)
        
        # 按钮容器
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(padx=5, pady=0, fill=tk.X)
        
        # 执行按钮
        exec_btn = ttk.Button(btn_frame, text="执行命令", command=self.execute_command, style="Accent.TButton")
        exec_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 清空输入按钮
        clear_input_btn = ttk.Button(btn_frame, text="清空输入", command=lambda: self.cmd_text.delete(1.0, tk.END))
        clear_input_btn.pack(side=tk.LEFT, padx=5, pady=5)

    def create_output_area(self, parent):
        """创建命令输出显示区域（带滚动条）"""
        frame = ttk.LabelFrame(parent, text="📜 命令执行输出")
        frame.pack(padx=0, pady=5, fill=tk.BOTH, expand=True)
        
        # 滚动文本框
        self.output_text = scrolledtext.ScrolledText(frame, font=("Consolas", 9), wrap=tk.WORD, height=20)
        self.output_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)  # 初始设为只读
        
        # 清空输出按钮
        clear_output_btn = ttk.Button(frame, text="清空输出", command=self.clear_output)
        clear_output_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def append_output(self, text, is_error=False):
        """向输出区追加文本（区分正常/错误信息）"""
        self.output_text.config(state=tk.NORMAL)
        # 错误信息标红，正常信息黑色
        if is_error:
            self.output_text.insert(tk.END, f"❌ {text}\n", "error")
        else:
            self.output_text.insert(tk.END, f"✅ {text}\n", "normal")
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("normal", foreground="black")
        self.output_text.see(tk.END)  # 自动滚动到末尾
        self.output_text.config(state=tk.DISABLED)

    def clear_output(self):
        """清空输出区内容"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def execute_command(self):
        """执行输入的Git命令"""
        command = self.cmd_text.get(1.0, tk.END).strip()
        if not command:
            self.append_output("请输入要执行的Git命令！", is_error=True)
            return
        
        # 拼接Git Bash执行命令（Windows下）
        # 尝试多个可能的Git Bash安装位置
        possible_paths = [
            "C:\\Program Files\\Git\\bin\\bash.exe",
            "C:\\Program Files (x86)\\Git\\bin\\bash.exe",
            "D:\\Program Files\\Git\\bin\\bash.exe",
            "D:\\Program Files (x86)\\Git\\bin\\bash.exe"
        ]
        
        git_bash_path = None
        for path in possible_paths:
            if os.path.exists(path):
                git_bash_path = path
                break
        
        # 如果没找到，尝试使用环境变量中的bash.exe
        if not git_bash_path:
            git_bash_path = "bash.exe"
        
        try:
            self.append_output(f"开始执行命令：{command}（工作目录：{self.working_dir}）", is_error=False)
            # 执行命令并捕获输出
            result = subprocess.run(
                [git_bash_path, "-c", command],
                cwd=self.working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                timeout=30  # 超时时间30秒
            )
            # 显示正常输出
            if result.stdout:
                self.append_output(f"执行结果：\n{result.stdout}", is_error=False)
            # 显示错误输出
            if result.stderr:
                self.append_output(f"错误信息：\n{result.stderr}", is_error=True)
            # 显示执行状态
            if result.returncode == 0:
                self.append_output(f"命令执行成功！返回码：{result.returncode}", is_error=False)
            else:
                self.append_output(f"命令执行失败！返回码：{result.returncode}", is_error=True)
        except subprocess.TimeoutExpired:
            self.append_output(f"命令执行超时（30秒）！", is_error=True)
        except FileNotFoundError:
            self.append_output(f"❌ 未找到Git Bash！", is_error=True)
            self.append_output(f"请按照以下步骤操作：", is_error=True)
            self.append_output(f"1. 从 https://git-scm.com/downloads 下载并安装Git", is_error=True)
            self.append_output(f"2. 安装时选择'Add Git to PATH'选项", is_error=True)
            self.append_output(f"3. 重启电脑后再运行本工具", is_error=True)
            self.append_output(f"4. 若已安装Git但仍报错，请手动修改代码中的possible_paths列表", is_error=True)
        except Exception as e:
            self.append_output(f"执行命令时发生异常：{str(e)}", is_error=True)

if __name__ == "__main__":
    # 设置tkinter样式
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use("clam")  # 美观的样式（兼容不同系统）
    # 自定义按钮样式
    style.configure("Accent.TButton", foreground="white", background="#0078d7")
    # 启动GUI
    app = GitBashGUI(root)
    root.mainloop()
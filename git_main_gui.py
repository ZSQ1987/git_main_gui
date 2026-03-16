import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import subprocess
import os
import sys

class GitBashGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("快速 Git Bash 工具 - Python 3.11.9 + ttk")
        
        # 初始窗口大小（增加宽度以适应双栏布局）
        window_width = 1000
        window_height = 600
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(800, 500)
        
        # 计算居中位置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 初始化工作目录
        self.working_dir = os.getcwd()
        
        # 初始化命令字典（空，全手动添加）
        self.create_commands = {}
        self.update_commands = {}
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding=(10, 10, 10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左右分栏布局
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # 左侧界面：选择目录，输入命令行，显示结果
        self.create_dir_selector(left_frame)
        self.create_custom_command_area(left_frame)
        self.create_output_area(left_frame)
        
        # 右侧界面：显示自定义GUI命令
        self.create_quick_commands(self.right_frame)

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
        
        close_btn = ttk.Button(btn_frame, text="关闭", command=help_window.destroy)
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
        
        # 排版创建命令按钮（每行1个）
        row = 0
        for btn_text, cmd in self.create_commands.items():
            # 创建按钮容器
            btn_frame = ttk.Frame(create_frame)
            btn_frame.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
            
            # 命令按钮
            btn = ttk.Button(btn_frame, text=btn_text, 
                             command=lambda c=cmd: self.fill_command(c),
                             width=30)  # 固定按钮宽度
            btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # 删除按钮
            delete_btn = ttk.Button(btn_frame, text="删除", 
                                   command=lambda bt=btn_text: self.delete_command(bt, "create"),
                                   style="Accent.TButton")
            delete_btn.pack(side=tk.RIGHT, padx=5)
            
            row += 1
        
        # 让列自适应宽度
        create_frame.grid_columnconfigure(0, weight=1)
        
        # 添加命令按钮
        add_create_btn = ttk.Button(create_frame, text="添加命令", command=lambda: self.add_custom_command("create"))
        add_create_btn.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # 更新命令区域
        update_frame = ttk.LabelFrame(parent, text="🔄 更新相关命令")
        update_frame.pack(padx=0, pady=5, fill=tk.X)
        
        # 排版更新命令按钮（每行1个）
        row = 0
        for btn_text, cmd in self.update_commands.items():
            # 创建按钮容器
            btn_frame = ttk.Frame(update_frame)
            btn_frame.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
            
            # 命令按钮
            btn = ttk.Button(btn_frame, text=btn_text, 
                             command=lambda c=cmd: self.fill_command(c),
                             width=30)  # 固定按钮宽度
            btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # 删除按钮
            delete_btn = ttk.Button(btn_frame, text="删除", 
                                   command=lambda bt=btn_text: self.delete_command(bt, "update"),
                                   style="Accent.TButton")
            delete_btn.pack(side=tk.RIGHT, padx=5)
            
            row += 1
        
        # 让列自适应宽度
        update_frame.grid_columnconfigure(0, weight=1)
        
        # 添加命令按钮
        add_update_btn = ttk.Button(update_frame, text="添加命令", command=lambda: self.add_custom_command("update"))
        add_update_btn.grid(row=row, column=0, padx=5, pady=5, sticky=tk.W+tk.E)

    def add_custom_command(self, command_type):
        """添加自定义命令"""
        # 创建添加命令的弹窗
        add_window = tk.Toplevel(self.root)
        add_window.title("添加自定义命令")
        add_window.geometry("400x200")
        add_window.resizable(False, False)
        
        # 居中显示
        add_window.transient(self.root)
        add_window.grab_set()
        
        # 计算居中位置
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        
        window_width = 400
        window_height = 200
        
        x = root_x + (root_width - window_width) // 2
        y = root_y + (root_height - window_height) // 2
        
        add_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建输入框架
        input_frame = ttk.Frame(add_window, padding=(20, 20, 20, 20))
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # 命令名称输入
        ttk.Label(input_frame, text="命令名称：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(input_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 命令内容输入
        ttk.Label(input_frame, text="命令内容：").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        cmd_var = tk.StringVar()
        cmd_entry = ttk.Entry(input_frame, textvariable=cmd_var, width=30)
        cmd_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 按钮框架
        btn_frame = ttk.Frame(add_window)
        btn_frame.pack(padx=20, pady=10, fill=tk.X)
        
        # 确认按钮
        def confirm_add():
            name = name_var.get().strip()
            cmd = cmd_var.get().strip()
            if name and cmd:
                if command_type == "create":
                    self.create_commands[name] = cmd
                else:
                    self.update_commands[name] = cmd
                add_window.destroy()
                # 重新创建命令按钮
                # 刷新右侧面板
                for widget in self.right_frame.winfo_children():
                    widget.destroy()
                self.create_quick_commands(self.right_frame)
            else:
                messagebox.showwarning("警告", "命令名称和内容不能为空！")
        
        confirm_btn = ttk.Button(btn_frame, text="确认添加", command=confirm_add, style="Accent.TButton")
        confirm_btn.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        cancel_btn = ttk.Button(btn_frame, text="取消", command=add_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def delete_command(self, btn_text, command_type):
        """删除自定义命令"""
        if command_type == "create":
            if btn_text in self.create_commands:
                del self.create_commands[btn_text]
        else:
            if btn_text in self.update_commands:
                del self.update_commands[btn_text]
        
        # 刷新右侧面板
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        self.create_quick_commands(self.right_frame)

    def fill_command(self, command):
        """将快捷命令填充到自定义输入框"""
        self.cmd_text.delete(1.0, tk.END)
        self.cmd_text.insert(tk.END, command)
        # 若为commit命令，将光标定位到引号中间
        if "git commit -m """ in command:
            self.cmd_text.focus()
            pos = len('git commit -m "')
            self.cmd_text.mark_set(tk.INSERT, f"1.0 + {pos} chars")

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
        self.output_text.config(state=tk.DISABLED)
        
        # 清空输出按钮
        clear_output_btn = ttk.Button(frame, text="清空输出", command=self.clear_output)
        clear_output_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def append_output(self, text, is_error=False):
        """向输出区追加文本（区分正常/错误信息）"""
        self.output_text.config(state=tk.NORMAL)
        if is_error:
            self.output_text.insert(tk.END, f"❌ {text}\n", "error")
        else:
            self.output_text.insert(tk.END, f"✅ {text}\n", "normal")
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("normal", foreground="black")
        self.output_text.see(tk.END)
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
        
        if not git_bash_path:
            git_bash_path = "bash.exe"
        
        try:
            self.append_output(f"开始执行命令：{command}（工作目录：{self.working_dir}")
            # 执行命令并捕获输出
            result = subprocess.run(
                [git_bash_path, "-c", command],
                cwd=self.working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                encoding="utf-8",
                timeout=30
            )
            if result.stdout:
                self.append_output(f"执行结果：\n{result.stdout}")
            if result.stderr:
                self.append_output(f"错误信息：\n{result.stderr}", is_error=True)
            if result.returncode == 0:
                self.append_output(f"命令执行成功！返回码：{result.returncode}")
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
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Accent.TButton", foreground="white", background="#0078d7")
    app = GitBashGUI(root)
    root.mainloop()
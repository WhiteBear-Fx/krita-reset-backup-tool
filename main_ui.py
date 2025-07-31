import shutil
import tkinter as tk
from tkinter import ttk
import sv_ttk
import darkdetect  # 系统主题检测
import datetime  # 用于获取当前日期时间
import os
import json_manage
from PIL import Image, ImageTk
import platform_dependence
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox

version = None
developer = None

# 全局常量：界面元素的内边距
PAD_X = 10
PAD_Y = 10

language_var_dic = {}


def import_language():
    global language_var_dic
    for key, value in list(json_manage.language_manager.get_data().items()):
        language_var_dic[key] = tk.StringVar(value=value)


def set_language(language):
    json_manage.language_manager.reload_for_language(language)
    for key, value in json_manage.language_manager.get_data().items():
        language_var_dic[key].set(value)


_style_callback = []


def set_style_callback(callback):
    _style_callback.append(callback)


def set_style(style: str):
    if style == 'dark':
        sv_ttk.use_dark_theme()

    if style == 'light':
        sv_ttk.use_light_theme()

    if style == 'sys':
        sv_ttk.set_theme(darkdetect.theme())

    for c in _style_callback:
        c()
    json_manage.settings_manager.set_setting('window_style', style)

def move_window_center(window: tk.Tk|tk.Toplevel):
    """将窗口移动到屏幕中心"""
    window.update_idletasks()  # 确保获取到最新窗口尺寸

    # 计算屏幕和窗口尺寸
    screen_height = window.winfo_screenheight()
    screen_width = window.winfo_screenwidth()
    window_height = window.winfo_height()
    window_width = window.winfo_width()

    # 设置窗口位置
    window.geometry(f'+{screen_width // 2 - window_width // 2}+{screen_height // 2 - window_height // 2}')


class RootWindow(tk.Tk):
    """主窗口类"""

    def __init__(self):
        super().__init__()

        import_language()
        # 窗口基本设置
        self.minsize(810, 700)
        self.title(json_manage.language_manager.get_static()['title'])
        self.iconbitmap(platform_dependence.get_app_icon())

        self.timer_id = None
        self.last_size = None

        self.geometry(json_manage.settings_manager.get_setting('window_size'))
        self.bind('<Configure>', self.on_resize)

        # 添加主界面
        self.main_window = MainWindow(self)
        self.main_window.pack(side='top', fill='both', expand=True, padx=PAD_X, pady=PAD_Y)

        # 应用主题
        # noinspection PyBroadException
        try:
            self.update_idletasks()
            set_style(json_manage.settings_manager.get_setting('window_style'))
        except:
            set_style('dark')

        # 应用标题栏主题
        # noinspection PyBroadException
        try:
            platform_dependence.apply_theme_to_titlebar(self)
        except:
            pass  # 忽略标题栏样式异常

        # 窗口居中并启动主循环
        move_window_center(self)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.mainloop()

    # noinspection PyTypeChecker,PyUnusedLocal
    def on_resize(self, event):
        # 忽略最小化状态下的调整
        if self.state() == 'normal':
            self.last_size = f"{self.winfo_width()}x{self.winfo_height()}"

    def on_closing(self):
        self.save_current_window_size()
        try:
            shutil.rmtree(os.path.join(os.getcwd(),'temp'))

        except FileNotFoundError:
            pass

        except Exception as e:
            messagebox.showerror(title=json_manage.language_manager.get_static()['error'],
                                 message = json_manage.language_manager.get_static()['error-temp-del-fail'].replace('{$e}', str(e)))
        self.destroy()

    def save_current_window_size(self):
        """保存当前窗口尺寸到设置"""
        # 确保窗口处于正常状态（非最小化/最大化）
        if self.state() == 'normal':
            json_manage.settings_manager.set_setting('window_size', self.last_size)
        self.timer_id = None  # 重置定时器ID


class MainWindow(ttk.Frame):
    """主界面容器"""

    def __init__(self, parent):
        super().__init__(parent)

        self.top_tool_bar = TopToolBar(self)
        self.top_tool_bar.pack(side='top', fill='x', expand=False, padx=PAD_X, pady=PAD_Y)

        # 配置列表和工具栏
        self.tool_bar = ToolBar(self)
        self.tool_bar.pack(side='bottom', fill='x', expand=False, padx=PAD_X, pady=PAD_Y)

        self.top_tool_bar.set_tool_bar(self.tool_bar)

        self.config_list = ConfigList(self, self.tool_bar)
        self.config_list.pack(side='top', fill='both', expand=True, padx=PAD_X, pady=PAD_Y)
        self.tool_bar.config_list = self.config_list
        self.top_tool_bar.config_list = self.config_list

        # 连接工具栏和配置列表
        self.tool_bar.add_button.config(command=self.show_add_dialog)
        self.tool_bar.del_button.config(command=self.config_list.delete_selected_configs)

    def show_add_dialog(self):
        """显示添加配置的对话框"""
        # 生成默认名称：当前系统日期时间（年月日时分秒）带连字符
        default_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        # 获取现有配置名称
        existing_names = self.config_list.get_all_config_names()

        # 创建自定义对话框
        dialog = AddConfigDialog(self.winfo_toplevel(), default_name, existing_names)
        name = dialog.result

        # 用户取消输入
        if name is None:
            return

        # 添加新配置
        success = self.config_list.add_config(name)
        if not success:
            self.tool_bar.show_error(json_manage.language_manager.get_static().get('error-name-conflict'))


# noinspection PyUnusedLocal
class KritaConfigIcon(ttk.Frame):
    """单个配置项的卡片视图 - 底部添加状态指示器"""

    # noinspection PyTypeChecker
    def __init__(self, parent, name, config_list, is_reset=False):
        super().__init__(parent, style='Card.TFrame', padding=5)  # 使用卡片样式

        # 存储名称和选中状态
        self.name = name
        self.is_reset = is_reset  # 标记是否是重置配置项
        self.selected = tk.BooleanVar(value=False)  # 状态变量
        self.config_list = config_list  # 引用配置列表

        # 主内容框架
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side='top', fill='both', expand=True)

        # 加载图标 - 重置配置项使用特殊图标
        icon_file = 'icon-null.png' if is_reset else 'icon.png'  # 修改为PNG文件
        icon_path = os.path.join(os.getcwd(), 'resources', icon_file)

        # 处理图标加载
        try:
            # 使用PIL打开并调整图像大小
            img = Image.open(icon_path)
            # 计算新尺寸（保持宽高比）
            width, height = img.size
            new_width = 100
            new_height = int(height * (new_width / width))
            img = img.resize((new_width, new_height))

            # 转换为PhotoImage
            self.icon_image = ImageTk.PhotoImage(img)
            self.icon = ttk.Label(self.content_frame, image=self.icon_image)
            self.icon.pack(side='top', padx=PAD_X, pady=PAD_Y)
        except Exception as e:
            print(f"无法加载图标: {e}")
            # 如果没有图标，使用文本替代
            icon_text = "[重置]" if is_reset else "[图标]"
            self.icon = ttk.Label(self.content_frame, text=icon_text)
            self.icon.pack(side='top', padx=PAD_X, pady=PAD_Y)

        self.label = ttk.Label(self.content_frame, text=name, wraplength=150)
        self.label.pack(side='top', padx=PAD_X, pady=PAD_Y)

        # 创建底部状态指示器（Canvas）
        self.indicator_height = 3  # 指示器高度
        self.indicator = tk.Canvas(
            self,
            height=self.indicator_height,
            highlightthickness=0,  # 去除高亮边框
        )
        self.indicator_color = None
        # 设置最小宽度（控制卡片最小宽度）
        self.indicator.config(width=160)
        self.indicator.pack(side='bottom', fill='x', pady=(5, 0))

        # 初始绘制透明指示器（占位）
        self.indicator_rect = self.indicator.create_rectangle(
            0, 0, 200, self.indicator_height,
            fill="",  # 透明填充
            outline=""  # 透明边框
        )

        # 为整个卡片内容添加点击事件处理
        self.bind("<Button-1>", self.toggle_selection)
        self.content_frame.bind("<Button-1>", self.toggle_selection)
        self.icon.bind("<Button-1>", self.toggle_selection)
        self.label.bind("<Button-1>", self.toggle_selection)
        self.indicator.bind("<Button-1>", self.toggle_selection)

    def toggle_selection(self, event=None):
        """切换选中状态，根据多选模式决定行为"""
        if not self.config_list.multi_select.get():
            # 单选模式：先取消所有选择
            self.config_list.deselect_all()

        # 切换当前卡片的选中状态
        self.selected.set(not self.selected.get())

        # 更新指示器状态
        self.update_indicator()
        return "break"  # 阻止事件继续传播

    def update_indicator(self):
        """更新指示器颜色状态"""
        if self.selected.get() and sv_ttk.get_theme() == "light":
            self.indicator.itemconfig(self.indicator_rect, fill="#0560b6")
        elif self.selected.get() and sv_ttk.get_theme() == "dark":
            self.indicator.itemconfig(self.indicator_rect, fill="#57c8ff")
        else:
            self.indicator.itemconfig(self.indicator_rect, fill="")

    def is_selected(self) -> bool:
        """返回当前配置是否被选中"""
        return self.selected.get()


# noinspection PyUnusedLocal
class ConfigList(ttk.Frame):
    """可滚动的配置列表容器"""

    def __init__(self, parent, tool_bar):
        super().__init__(parent)
        self.tool_bar = tool_bar

        # 创建画布和滚动条
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(side='left', fill='both', expand=True)

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='left', fill='y', expand=False)

        # 内部框架（实际内容容器）
        self.frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(0, 0, window=self.frame, anchor='nw')  # 左上角对齐

        # 配置存储和ID管理
        self.config_dic = {}
        self.config_id = 0

        # 多选模式开关
        self.multi_select = tk.BooleanVar(value=False)
        self.tool_bar.multi_select_switch.config(variable=self.multi_select)

        # 添加特殊重置配置项
        self.add_reset_config()

        # 绑定尺寸变化事件
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.frame.bind("<Configure>", self.on_frame_configure)

        set_style_callback(self._update_all_cards)

        self._add_config_with_config()

    def _add_config_with_config(self):
        configs = json_manage.config_manager.get_all_configs()
        for config in configs.keys():
            self._add_config(config)

    def add_reset_config(self):
        """添加特殊重置配置项"""
        reset_name = json_manage.language_manager.get_static()['clear']
        reset_config = KritaConfigIcon(self.frame, reset_name, self, is_reset=True)

        # 使用特殊ID 0 表示重置配置项
        self.config_dic[0] = reset_config
        self.config_id = max(self.config_id, 1)  # 确保普通配置ID从1开始

        # 刷新布局
        self.frame.update_idletasks()
        self.on_frame_configure(None)
        self.arrange_data_cards()

    def on_canvas_configure(self, event):
        """调整画布大小时更新内部框架宽度"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_frame_configure(self, event):
        """更新滚动区域并保持顶部位置"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.arrange_data_cards()

    def _add_config(self, name=None):
        """添加新配置项到列表"""
        # 如果没有提供名称，则使用默认名称
        if name is None:
            # 生成默认名称：当前系统日期时间（年月日时分秒）带连字符
            default_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            name = default_name

        config = KritaConfigIcon(self.frame, name, self)

        # 使用递增ID确保新项目有最大的索引
        self.config_id += 1
        self.config_dic[self.config_id] = config

        # 刷新布局并更新滚动区域
        self.frame.update_idletasks()
        self.on_frame_configure(None)
        self.canvas.yview_moveto(0.0)  # 新建后从顶部开始显示

        # 立即排列卡片，确保新卡片在最前面
        self.arrange_data_cards()
        return True, self.config_id

    def input_config(self, path, new_name=None):
        platform_dependence.input_krita_config(path, new_name)
        self._add_config(new_name)

    def add_config(self, name=None):
        """
            添加新配置项到UI列表和文件系统

            返回值:
                (bool, int|str):
                    - 成功时: (True, 新配置ID)
                    - 失败时: (False, 错误消息)

            处理流程:
                1. 先在UI中添加配置项
                2. 成功后尝试在文件系统创建配置
                3. 若文件系统创建失败则回滚UI添加操作
            """
        is_add = self._add_config(name)
        if is_add:
            _is_add = platform_dependence.new_krita_config(name)
            if not _is_add[0]:
                self.config_dic.pop(is_add[1]).destroy()
                return _is_add
        return is_add

    def delete_selected_configs(self):
        """删除所有选中的配置项"""
        # 找出所有选中的配置ID
        selected_ids = [
            config_id for config_id, config in self.config_dic.items()
            if config.is_selected() and config_id != 0  # 排除重置配置项
        ]

        # 检查是否选中了重置配置项
        reset_selected = self.config_dic[0].is_selected() if 0 in self.config_dic else False
        if reset_selected:
            # 显示错误消息
            self.tool_bar.show_error(json_manage.language_manager.get_static()['error-del-re'])
            return

        if not selected_ids:
            return  # 如果没有选中的配置，直接返回

        # 删除选中的配置项
        for config_id in selected_ids:
            config = self.config_dic[config_id]
            if platform_dependence.del_krita_config(config.name):
                self.config_dic.pop(config_id)
                config.destroy()  # 从界面移除

        # 刷新布局
        self.frame.update_idletasks()
        self.on_frame_configure(None)

        # 重新排列卡片
        self.arrange_data_cards()

    def _update_all_cards(self):
        for c in self.config_dic.values():
            c.update_indicator()

    def deselect_all(self):
        """取消所有卡片的选中状态"""
        for config in self.config_dic.values():
            config.selected.set(False)
            config.update_indicator()

    def get_selected_configs(self) -> dict:
        """获取所有选中的配置项"""
        return {key : config for key, config in self.config_dic.items() if config.is_selected()}

    def get_all_config_names(self):
        """获取所有配置项的名称（排除重置配置项）"""
        return [config.name for config_id, config in self.config_dic.items() if config_id != 0]

    def is_name_exists(self, name: str) -> bool:
        """检查指定名称是否已存在（排除重置配置项）"""
        return name in self.get_all_config_names()

    def arrange_data_cards(self):
        self.canvas.update_idletasks()
        config_cards = list(self.config_dic.values())

        # 清除所有现有的网格布局
        for child in self.frame.winfo_children():
            child.grid_forget()

        if len(config_cards) > 0:
            # 获取当前画布宽度以计算每行可容纳的卡片数量
            canvas_width = self.canvas.winfo_width()
            card_width = []
            for i in config_cards:
                card_width.append(i.winfo_width())
            card_width = max(card_width) + PAD_X * 2

            # 计算每行可容纳的卡片数量，但至少为1
            number_per_row = max(1, canvas_width // card_width)

            # 确保重置配置项始终排在最前面
            # 分离重置配置项和其他配置项
            reset_card = None
            other_cards = []

            for card in config_cards:
                if card.is_reset:
                    reset_card = card
                else:
                    other_cards.append(card)

            # 按ID降序排列其他卡片（新卡片排在最前面）
            other_cards_sorted = sorted(
                other_cards,
                key=lambda c: list(self.config_dic.keys())[list(self.config_dic.values()).index(c)],
                reverse=True  # 降序排列
            )

            # 将所有卡片组合在一起，重置卡放在最前面
            all_cards = []
            if reset_card:
                all_cards.append(reset_card)
            all_cards.extend(other_cards_sorted)

            # 排列所有卡片
            for i, card in enumerate(all_cards):
                row = i // number_per_row
                col = i % number_per_row
                card.grid(row=row, column=col, padx=PAD_X, pady=PAD_Y, sticky='nsew')


class AddConfigDialog(tk.Toplevel):
    """自定义添加配置对话框 - 使用ttk控件"""

    def __init__(self, parent, default_name, existing_names, text=None):
        super().__init__(parent)
        self.transient(parent)  # 设置为父窗口的临时窗口
        self.title(json_manage.language_manager.get_static()['title-new'])
        self.resizable(False, False)

        # 存储现有配置名称
        self.existing_names = existing_names

        # 对话框内容框架
        self.frame = ttk.Frame(self, padding=(PAD_X * 2, PAD_Y * 2))
        self.frame.pack(fill='both', expand=True)

        # 存储结果
        self.result = None

        # 错误标签 - 放在顶部
        self.error_label = ttk.Label(
            self.frame,
            text="",
            foreground="red",
            font=("Arial", 9, "bold")
        )
        self.error_label.pack(anchor='w', padx=PAD_X, pady=(0, PAD_Y))

        # 标签和输入框
        if text:
            ttk.Label(self.frame, text=text).pack(anchor='w', padx=PAD_X, pady=PAD_Y)
        ttk.Label(self.frame, textvariable=language_var_dic['ask-name']).pack(anchor='w', padx=PAD_X, pady=PAD_Y)

        self.name_var = tk.StringVar(value=default_name)
        self.name_entry = ttk.Entry(self.frame, textvariable=self.name_var)
        self.name_entry.pack(fill='x', padx=PAD_X, pady=(0, PAD_Y * 2))
        self.name_entry.select_range(0, tk.END)  # 默认全选文本
        self.name_entry.focus_set()  # 设置焦点

        # 按钮框架 - 使用Frame来容纳按钮
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill='x', padx=PAD_X, pady=(PAD_Y, 0))

        # 取消按钮 - 放在左边
        self.cancel_button = ttk.Button(
            button_frame,
            textvariable=language_var_dic['cancel'],
            command=self.cancel_clicked
        )
        self.cancel_button.pack(side='left', padx=(0, PAD_X))

        # 确定按钮 - 放在右边
        self.ok_button = ttk.Button(
            button_frame,
            textvariable=language_var_dic['ok'],
            style='Accent.TButton',
            command=self.ok_clicked
        )
        self.ok_button.pack(side='right')

        # 绑定回车键
        self.bind("<Return>", lambda e: self.ok_clicked())

        # 设置窗口居中
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.geometry(f"+{x}+{y}")

        # 设置为模态对话框
        self.grab_set()
        self.wait_window(self)

    def ok_clicked(self):
        """确定按钮点击处理"""
        name = self.name_var.get().strip()

        # 检查名称是否为空
        if not name:
            self.show_error(json_manage.language_manager)
            return

        # 检查名称是否已存在
        if name in self.existing_names:
            self.show_error(json_manage.language_manager.get_static().get('error-name-conflict').replace('{$name}', name))
            return

        # 所有检查通过
        self.result = name
        self.destroy()

    def cancel_clicked(self):
        """取消按钮点击处理"""
        self.result = None
        self.destroy()

    def show_error(self, message: str):
        """显示错误消息"""
        self.error_label.config(text=message)


class ToolBar(ttk.Frame):
    """底部工具栏 - 添加多选开关和应用验证"""

    def __init__(self, parent):
        super().__init__(parent, style='Card.TFrame')  # 卡片样式
        self.config_list = None  # 将在MainWindow中设置
        self.error_label = None  # 错误提示标签
        self.error_timer = None  # 错误提示计时器

        # 添加配置按钮
        self.add_button = ttk.Button(
            self,
            text='+',
            style='Accent.TButton',
            width=1
        )
        self.add_button.pack(side='left', fill='x', expand=False, padx=PAD_X, pady=PAD_Y)

        # 删除配置按钮
        self.del_button = ttk.Button(
            self,
            text='-',
            style='Accent.TButton',
            width=1
        )
        self.del_button.pack(side='left', fill='x', expand=False, padx=PAD_X, pady=PAD_Y)

        # 多选开关
        self.multi_select_frame = ttk.Frame(self)
        self.multi_select_frame.pack(side='left', fill='x', expand=False, padx=PAD_X, pady=PAD_Y)

        self.multi_select_label = ttk.Label(self.multi_select_frame, textvariable=language_var_dic['multi'])
        self.multi_select_label.pack(side='left', padx=(0, 5))

        self.multi_select_switch = ttk.Checkbutton(
            self.multi_select_frame,
            style='Switch.TCheckbutton',
            command=self.on_multi_select_changed  # 添加状态改变回调
        )
        self.multi_select_switch.pack(side='left')

        # 错误提示标签容器（初始为空）
        self.error_container = ttk.Frame(self)
        self.error_container.pack(side='left', fill='x', expand=True, padx=(0, PAD_X))

        # 应用配置按钮
        self.use_button = ttk.Button(
            self,
            textvariable=language_var_dic.get('apply'),
            style='Accent.TButton',
            command=self.apply_configuration
        )
        self.use_button.pack(side='right', fill='x', expand=False, padx=(0, PAD_X), pady=PAD_Y)

        # 添加Krita进程状态指示器
        self.krita_status_frame = ttk.Frame(self)
        self.krita_status_frame.pack(side='right', fill='x', expand=False, padx=(0, PAD_X), pady=PAD_Y)

        self.krita_status_label = ttk.Label(
            self.krita_status_frame,
            textvariable=language_var_dic['state-ex'],
            font=("Arial", 9)
        )
        self.krita_status_label.pack(side='left', padx=(0, 5))

        self.krita_status_indicator = ttk.Label(
            self.krita_status_frame,
            text="●",  # 圆形指示器
            foreground="gray",  # 默认灰色
            font=("Arial", 10, "bold")
        )
        self.krita_status_indicator.pack(side='left')

        # 启动后台线程检查Krita状态
        self.update_krita_status()

    def on_multi_select_changed(self):
        """多选开关状态改变时的回调函数"""
        if not self.config_list:
            return

        # 当切换到单选模式时取消所有选择
        if not self.config_list.multi_select.get():
            self.config_list.deselect_all()

    def update_krita_status(self):
        """在后台线程中更新Krita状态"""
        platform_dependence.set_krita_is_on_callback(lambda: self.update_status_ui(True))
        platform_dependence.set_krita_is_off_callback(lambda: self.update_status_ui(False))
        platform_dependence.set_krita_is_unk_callback(lambda: self.update_status_ui(None))

        platform_dependence.update_krita_status()


    def update_status_ui(self, is_running):
        """更新Krita状态UI"""
        if is_running is None:
            # 检查失败
            self.krita_status_label.config(textvariable=language_var_dic['state-unk'])
            self.krita_status_indicator.config(foreground="gray")
        elif is_running:
            # Krita正在运行
            self.krita_status_label.config(textvariable=language_var_dic['state-on'])
            self.krita_status_indicator.config(foreground="#FF5252")  # 红色
        else:
            # Krita未运行
            self.krita_status_label.config(textvariable=language_var_dic['state-off'])
            self.krita_status_indicator.config(foreground="#4CAF50")  # 绿色

    def check_selected_items(self):
        # 获取选中的配置项
        if not self.config_list:
            self.show_error("配置列表未初始化！")
            return False

        selected_configs = self.config_list.get_selected_configs()
        num_selected = len(selected_configs)

        if num_selected == 0:
            self.show_error(json_manage.language_manager.get_static()['error-no-selection'])
            return False

        if num_selected > 1:
            self.show_error(json_manage.language_manager.get_static()['error-select-conflict'])
            return False
        return True

    def apply_configuration(self):
        """应用配置验证逻辑"""
        # 检查Krita是否正在运行
        # noinspection PyBroadException
        is_run = platform_dependence.check_krita()
        if is_run:
            self.show_error(json_manage.language_manager.get_static().get('error-krita-is-on'))
            return
        if is_run is None:
            # 如果检查失败，尝试应用配置
            self.show_error(json_manage.language_manager.get_static().get('error-krita-is-unk'))

        if self.check_selected_items():
            # 只有一个配置被选中，执行应用逻辑
            selected_configs = self.config_list.get_selected_configs()
            if list(selected_configs.keys())[0] == 0:
                config = list(selected_configs.values())[0]
                self._use(config, True)
            else:
                config = list(selected_configs.values())[0]

                # 清除任何现有的错误消息
                self.clear_error()

                if not platform_dependence.check_configuration_path(config.name):
                    ask_window = AskWindow(self.winfo_toplevel(),
                                           text=json_manage.language_manager.get_static().get('path_disagreement')
                                           .replace('{$PATH}', platform_dependence.get_config_path(config.name)[1]))
                    ask_window.set_ok_callback(lambda :self._use(config))
                    ask_window.set_cancel_callback(ask_window.destroy)
                    return
                self._use(config)

    def _use(self, config, reset=False):
        if reset:
            is_use = platform_dependence.reset_krita()
        else:
            is_use = platform_dependence.use_krita_config(config.name)
        if is_use:
            self.show_success(json_manage.language_manager.get_static().get('apply-done').replace('{$name}', config.name))

        # 这里添加实际的应用配置逻辑
        # print(f"正在应用配置: {config.name}")

    def show_error(self, message: str):
        """显示错误提示消息，5秒后消失"""
        # 清除之前的错误提示和计时器
        if self.error_timer:
            self.after_cancel(self.error_timer)
            self.error_timer = None

        # 销毁之前的错误标签
        if self.error_label:
            self.error_label.destroy()

        # 创建新的错误提示标签
        self.error_label = ttk.Label(
            self.error_container,
            text=message,
            foreground="red",
            font=("Arial", 9, "bold")
        )
        self.error_label.pack(side='right', padx=(0, 10))

        # 设置5秒后自动消失
        # noinspection PyTypeChecker
        self.error_timer = self.after(5000, self.clear_error)

    def show_success(self, message: str):
        """显示成功提示消息（蓝色），5秒后消失"""
        # 清除之前的错误提示和计时器
        if self.error_timer:
            self.after_cancel(self.error_timer)
            self.error_timer = None

        # 销毁之前的错误标签
        if self.error_label:
            self.error_label.destroy()

        # 创建新的成功提示标签
        self.error_label = ttk.Label(
            self.error_container,
            text=message,
            foreground="#3CCAF5",
            font=("Arial", 9, "bold")
        )
        self.error_label.pack(side='right', padx=(0, 10))

        # 设置5秒后自动消失
        # noinspection PyTypeChecker
        self.error_timer = self.after(5000, self.clear_error)

    def clear_error(self):
        """清除错误提示"""
        if self.error_label:
            self.error_label.destroy()
            self.error_label = None
        self.error_timer = None


class TopToolBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # 保存父窗口引用（通常是根窗口）
        self.root = parent.winfo_toplevel()
        self.tool_bar = None
        self.config_list = None

        self.input_button = ttk.Button(
            self,
            textvariable=language_var_dic['input'],
            command=self.input_on_click  # 添加点击事件绑定
        )
        self.input_button.pack(side='left', padx=PAD_X)

        self.output_button = ttk.Button(
            self,
            textvariable=language_var_dic['output'],
            command=self.output_on_click  # 添加点击事件绑定
        )
        self.output_button.pack(side='left', padx=PAD_X)

        self.setting_button = ttk.Button(
            self,
            textvariable=language_var_dic['setting'],
            command=self.setting_on_click  # 添加点击事件绑定
        )
        self.setting_button.pack(side='right', padx=PAD_X)



        # 跟踪设置窗口实例
        self.setting_window = None

    def setting_on_click(self):
        """打开设置窗口"""
        # 防止重复打开
        if self.setting_window is not None and self.setting_window.winfo_exists():
            self.setting_window.lift()  # 如果已存在则提到前台
            return

        # 创建设置窗口，传递根窗口作为父窗口
        self.setting_window = SettingWindow(self.root)

        # 设置关闭时的回调
        self.setting_window.protocol("WM_DELETE_WINDOW", self.on_setting_close)

    def on_setting_close(self):
        """设置窗口关闭时的处理"""
        self.setting_window.destroy()
        self.setting_window = None

    def set_tool_bar(self, tool_bar: ToolBar):
        self.tool_bar = tool_bar

    def output_on_click(self):
        if self.tool_bar.check_selected_items():
            selected_configs = self.tool_bar.config_list.get_selected_configs()
            name = next(iter(selected_configs.values())).name
            if next(iter(selected_configs.keys())) == 0:
                self.tool_bar.show_error(json_manage.language_manager.get_static().get('error-output-reset')
                                         .replace('{$name}', name))
                return
            path = filedialog.asksaveasfilename(defaultextension='.zip', filetypes=(('zip', '*.zip'),), initialfile=name)
            if path:
                ask_window = AskWindow(self.root, text_variable=language_var_dic['on-output'], button_dis=True)
                ask_window.update_idletasks()
                platform_dependence.output_krita_config(name, path)
                ask_window.destroy()

    def input_on_click(self):
        path = filedialog.askopenfilename(defaultextension='.zip', filetypes=(('zip', '*.zip'),))
        if path:
            config_path, config_platform, config_name, file_path = platform_dependence.extract_krita_config(path)

            if config_platform != platform_dependence.get_platform_name():
                ask_window = AskWindow(self.winfo_toplevel(),
                                       text=json_manage.language_manager.get_static().get('error-platform-conflict')
                                       .replace('{$name}', config_name)
                                       .replace('{#config-platform}', config_platform)
                                       .replace('{#platform}', platform_dependence.get_platform_name()))
                ask_window.set_cancel_callback(ask_window.destroy)
                ask_window.set_ok_callback(ask_window.destroy)
                return
            if config_name in json_manage.config_manager.get_all_configs().keys():
                names = (name for name in json_manage.config_manager.get_all_configs().keys())
                default_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                new_name = AddConfigDialog(self.root, default_name, names,
                                           text=json_manage.language_manager.get_static().get('input-name_disagreement')
                                           .replace('{$name}', config_name))
                config_name = new_name.result
            if config_name:
                self.config_list.input_config(file_path, config_name)

class SettingWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(json_manage.language_manager.get_static().get('title-setting'))
        self.resizable(False, False)

        # 模态窗口设置（可选）
        self.grab_set()  # 阻止与其他窗口交互
        self.transient(parent)  # 始终显示在父窗口上方

        self.frame = ttk.Frame(self)
        self.frame.pack(side='top', fill='both', expand=True, padx=PAD_X, pady=PAD_Y)

        self.style_label = ttk.Label(self.frame, textvariable=language_var_dic.get('style-setting'))
        self.style_label.grid(column=0, row=0, padx=PAD_X, pady=PAD_Y, sticky='w')

        self.style_var = tk.StringVar(value=json_manage.settings_manager.get_setting('window_style'))

        self.style_d_rb = ttk.Radiobutton(self.frame, textvariable=language_var_dic.get('style-dark'), value='dark',
                                          variable=self.style_var,
                                          command=lambda: self.set_style(self.style_var, self.master))
        self.style_d_rb.grid(column=1, row=0, padx=PAD_X, pady=PAD_Y, sticky='w')

        self.style_l_rb = ttk.Radiobutton(self.frame, textvariable=language_var_dic.get('style-light'), value='light',
                                          variable=self.style_var,
                                          command=lambda: self.set_style(self.style_var, self.master))
        self.style_l_rb.grid(column=2, row=0, padx=PAD_X, pady=PAD_Y, sticky='w')

        self.style_sys_rb = ttk.Radiobutton(self.frame, textvariable=language_var_dic.get('style-sys'), value='sys',
                                            variable=self.style_var,
                                            command=lambda: self.set_style(self.style_var, self.master))
        self.style_sys_rb.grid(column=3, row=0, padx=PAD_X, pady=PAD_Y, sticky='w')

        self.lang_label = ttk.Label(self.frame, textvariable=language_var_dic.get('language'))
        self.lang_label.grid(column=0, row=1, padx=PAD_X, pady=PAD_Y, sticky='w')

        self.lang_cb = ttk.Combobox(self.frame, state='readonly')
        self.lang_cb.grid(column=1, row=1, padx=PAD_X, pady=PAD_Y, sticky='w', columnspan=3)

        self.lang_cb.configure(values=list(json_manage.language_manager.scan_language_files().keys()))
        self.lang_cb.set(json_manage.language_manager.get_meta().get('name'))

        self.lang_tip = ttk.Label(self.frame, textvariable=language_var_dic.get('language-tip'))
        self.lang_tip.grid(column=1, row=2, padx=PAD_X, pady=PAD_Y, sticky='w', columnspan=3)

        self.lang_cb.bind("<<ComboboxSelected>>",
                          lambda e: self.set_language())

        self.k_r_label = ttk.Label(self.frame, textvariable=language_var_dic.get('krita-resource-path'))
        self.k_r_label.grid(column=0, row=3, padx=PAD_X, pady=PAD_Y, sticky='w')

        self.k_r_var = tk.StringVar(value=json_manage.settings_manager.get_setting('krita_resources_path'))
        # 添加trace监控变量变化
        self.k_r_var.trace_add("write", self._auto_save_path)

        # 输入框
        self.k_r_entry = ttk.Entry(self.frame, textvariable=self.k_r_var, width=40)
        self.k_r_entry.grid(column=1, row=3, padx=PAD_X, pady=PAD_Y, sticky='we', columnspan=2)

        # 浏览按钮
        self.k_r_button = ttk.Button(
            self.frame,
            textvariable=language_var_dic.get('krita-resource-button'),
            command=self.browse_krita_directory
        )
        self.k_r_button.grid(column=3, row=3, padx=PAD_X, pady=PAD_Y, sticky='w')

        self.use_default_var = tk.BooleanVar(value=json_manage.settings_manager.get_setting('use_default_path'))
        self.ues_default_button = ttk.Checkbutton(self.frame, textvariable=language_var_dic.get('ues-default-button'),
                                                  variable=self.use_default_var, command=self.ues_default_button_on)
        self.ues_default_button.grid(column=4, row=3, padx=PAD_X, pady=PAD_Y, sticky='w')

        self.update_idletasks()
        self.k_r_tips = ttk.Label(self.frame,
                                  textvariable=language_var_dic.get('krita-resource-path-tips'))
        self.k_r_tips.grid(column=1, row=4, padx=PAD_X, pady=PAD_Y, sticky='we', columnspan=4)

        self.about_frame = ttk.LabelFrame(self.frame, text=json_manage.language_manager.get_static().get('about-title'))
        self.about_frame.grid(column=0, row=5, padx=PAD_X, pady=PAD_Y, columnspan=5, sticky='nsew')

        self.about_label_l = ttk.Label(self.about_frame, text=json_manage.language_manager.get_static().get('about-label-l')
                                     .replace('{$version}', version)
                                     .replace('{$developer}', developer),
                                     anchor='center')

        self.about_label_l.pack(side='left', fill='x', padx=PAD_X * 2, pady=PAD_Y * 2, expand=True)

        self.about_label_r = ttk.Label(self.about_frame, text=json_manage.language_manager.get_static().get('about-label-r')
                                     .replace('{$version}', version)
                                     .replace('{$developer}', developer),
                                     anchor='center')

        self.about_label_r.pack(side='left', fill='x', padx=PAD_X * 2, pady=PAD_Y * 2, expand=True)

        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()

        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.geometry(f"+{x}+{y}")

        platform_dependence.apply_theme_to_titlebar(self)

    def set_style(self, style_var, root):
        set_style(style_var.get())
        platform_dependence.apply_theme_to_titlebar(self)
        platform_dependence.apply_theme_to_titlebar(root)

    def set_language(self):
        lang_path = json_manage.language_manager.scan_language_files().get(self.lang_cb.get())
        set_language(lang_path)

    def browse_krita_directory(self):
        """打开文件夹选择对话框让用户选择Krita资源目录"""
        initial_dir = self.k_r_var.get() or os.path.expanduser("~")
        dir_path = filedialog.askdirectory(
            title=json_manage.language_manager.get_static().get('select-krita-resources'),
            initialdir=initial_dir
        )

        if dir_path:  # 确保用户没有取消选择
            self.k_r_var.set(dir_path)  # 设置变量会自动触发保存

    def _auto_save_path(self, *args):
        """当路径变量变化时自动保存到配置文件"""
        path = self.k_r_var.get()
        if path:  # 确保路径不为空
            current_setting = json_manage.settings_manager.get_setting('krita_resources_path')
            if path != current_setting:  # 只有当路径改变时才保存
                json_manage.settings_manager.set_setting('krita_resources_path', path)
                print(f"[INFO] Krita资源路径已更新为: {path}")
                json_manage.settings_manager.set_setting('use_default_path', False)
                self.use_default_var.set(False)

    def ues_default_button_on(self):
        if self.use_default_var.get():
            json_manage.settings_manager.set_setting('use_default_path', True)
            json_manage.settings_manager.set_setting('krita_resources_path',
                                                     json_manage.settings_manager.get_setting('default_path'))
            self.k_r_var.set(json_manage.settings_manager.get_setting('default_path'))
        else:
            json_manage.settings_manager.set_setting('use_default_path', False)

class AskWindow(tk.Toplevel):
    def __init__(self, master,text=None, text_variable=None, button_dis=False):
        tk.Toplevel.__init__(self, master, padx=PAD_X, pady=PAD_Y)

        self.grab_set()

        self.resizable(False, False)

        self.label = ttk.Label(self, wraplength=200, width=30, anchor='center')

        if text:
            self.label.configure(text=text)
        elif text_variable:
            self.label.configure(textvariable=text_variable)

        self.label.grid(column=0, row=0, padx=PAD_X, pady=PAD_Y, columnspan=2, sticky='nesw')

        if not button_dis:

            self.ok_button = ttk.Button(self, textvariable=language_var_dic.get('ok'))
            self.ok_button.grid(column=1, row=1, padx=PAD_X, pady=PAD_Y)

            self.cancel_button = ttk.Button(self, textvariable=language_var_dic.get('cancel'))
            self.cancel_button.grid(column=0, row=1, padx=PAD_X, pady=PAD_Y)

        platform_dependence.apply_theme_to_titlebar(self)

        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()

        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.geometry(f"+{x}+{y}")


    def set_ok_callback(self, callback):
        if self.ok_button:
            self.ok_button.configure(command=callback)

    def set_cancel_callback(self, callback):
        if self.cancel_button:
            self.cancel_button.configure(command=callback)



if __name__ == '__main__':
    root_window = RootWindow()  # 启动应用

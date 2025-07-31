import json
import os
import platform_dependence


class JsonManage:
    def __init__(self):
        self.settings = {}
        self.default_settings = {}
        self.settings_path = None

    def _load_settings(self):
        """加载设置文件，如果文件不存在则创建"""
        # 确保设置目录存在
        settings_dir = os.path.dirname(self.settings_path)
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir, exist_ok=True)

        # 如果文件不存在，创建并写入默认设置
        if not os.path.exists(self.settings_path):
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.default_settings, f, ensure_ascii=False, indent=4)

        # 加载设置
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        except Exception as e:
            print(f"加载设置失败: {str(e)}")
            self.settings = self.default_settings.copy()

    def set_default_settings(self, default_settings):
        """设置默认配置"""
        self.default_settings = default_settings.copy()

    def set_settings_path(self, settings_path):
        """设置配置文件路径并加载配置"""
        self.settings_path = settings_path
        self._load_settings()

    def get_setting(self, setting_name):
        """获取单个配置项"""
        return self.settings.get(setting_name, self.default_settings.get(setting_name))

    def get_all_settings(self):
        """获取所有配置项"""
        return self.settings.copy()

    def set_setting(self, setting_name, value):
        """更新单个配置项并保存"""
        self.settings[setting_name] = value
        self.save_settings()

    def update_settings(self, new_settings):
        """批量更新配置项并保存"""
        self.settings.update(new_settings)
        self.save_settings()

    def save_settings(self):
        """保存当前设置到文件"""
        if not self.settings_path:
            raise ValueError("设置路径未指定")

        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存设置失败: {str(e)}")
            return False

    def reset_to_defaults(self):
        """重置为默认设置"""
        self.settings = self.default_settings.copy()
        self.save_settings()


class SettingsManager(JsonManage):
    def __init__(self):
        super().__init__()

        # 定义默认设置
        default_settings = {
            'window_size': '780x620',
            'window_style': 'sys',
            'window_language': 'ZH',
            'krita_resources_path':platform_dependence.get_default_k_r_path(),
            'use_default_path': True,
            'default_path': platform_dependence.get_default_k_r_path(),
            'first_begin': True
        }

        # 设置默认配置和路径
        self.set_default_settings(default_settings)

        # 创建设置目录路径
        settings_dir = os.path.join(os.getcwd(), 'setting')
        settings_path = os.path.join(settings_dir, 'settings.json')

        # 加载设置
        self.set_settings_path(settings_path)
        self._update_default_k_r_path()

    def _update_default_k_r_path(self):
        if self.get_setting('default_path') != platform_dependence.get_default_k_r_path():
            self.set_setting('default_path', platform_dependence.get_default_k_r_path())

        if self.get_setting('use_default_path') and self.get_setting('krita_resources_path') != platform_dependence.get_default_k_r_path():
            self.set_setting('krita_resources_path', platform_dependence.get_default_k_r_path())

settings_manager = SettingsManager()

class LangManager(JsonManage):
    def __init__(self):
        super().__init__()

        # lang_code是文件名（无扩展名），name是显示名
        default_settings = {
            'meta': {
                'name': '简体中文'
            },
            'data': {
                'setting': '设置',
                'output':'导出',
                'on-output':'正在导出',
                'input':'导入',
                'apply': '应用',
                'state-off': 'Krita状态: 未运行',
                'state-on': 'Krita状态: 运行中',
                'state-ex': 'Krita状态: 检查中...',
                'state-unk':'Krita状态: 未知',
                'multi': '多选',
                'style-setting': '主题设置: ',
                'style-dark': '深色',
                'style-light': '浅色',
                'style-sys': '系统',
                'language': '语言: ',
                'ask-name':'请输入配置名称: ',
                'cancel':'取消',
                'ok':'确定',
                "language-tip":"修改语言后某些字符需要重启才会生效",
                'krita-resource-path': 'krita资源文件夹路径: ',
                'ues-default-button':'使用默认',
                'krita-resource-path-tips':'资源目录也属于配置项的一部分，此处的设置需要与krita的设置保持一致',
                'krita-resource-button':'浏览'
            },
            'static':{
                'about-title':'关于',
                'about-label-l':'版本: {$version}\n作者: {$developer}',
                'about-label-r':'中文语言文件提供者：白熊Fx\n(其他语言提供者切换语言后可看)',
                'title': 'krita配置管理工具',
                'clear': '重置/清空配置',
                'error':'错误',
                'error-temp-del-fail':'删除临时文件(程序根目录/temp)失败，因为{$e}，请手动删除。',
                'error-name-conflict':'配置名称\'{$name}\'已存在！',
                'error-output-reset':'配置组\'{$name}\'不可被导出！',
                'error-del-re':'重置配置项不可被删除',
                'error-name-empty':'配置名称不能为空！',
                'error-krita-is-on':'请先关闭Krita后再应用配置！',
                'error-no-selection':'请先选择一个配置！',
                'error-select-conflict':'该操作只能选择一个配置组！',
                'title-new':'新建配置',
                'apply-done':'正在应用配置: \'{$name}\'',
                'title-setting':'设置',
                'error-krita-is-unk':'无法确定krita是否运行，正在尝试应用配置',
                'platform_unk':'您使用的平台尚未支持',
                'path_disagreement':'该配置组的配置目录设置与当前的应用设置不同，您确定要应用吗？'
                                    '\n\n点击确定后程序的配置位置选项将被修改成\n\n{$PATH}',
                'input-name_disagreement':'该配置组命名\'{$name}\'，与已有配置组重复，请重命名',
                'error-platform-conflict':'无法导入：该配置组\'{$name}\'，来自\'{#config-platform}\'平台，'
                                          '与您使用的\'{#platform}\'不同，暂时不支持转换'

            }
        }

        self.set_default_settings(default_settings)
        self.language_dir = os.path.join(os.getcwd(), 'language')
        self.set_settings_path(self.get_current_lang_path())

    def get_current_lang_path(self):
        """获取当前语言对应的文件路径"""
        lang_code = settings_manager.get_setting('window_language')
        # lang_code来源自设定管理器的语言设置项，该设置项来源于本类扫描的语言
        return os.path.join(self.language_dir, f'{lang_code}.json')

    def scan_language_files(self):
        """
        扫描语言目录下的所有JSON文件
        返回字典格式: {语言名称: 文件路径}
        """
        lang_dict = {}
        if not os.path.exists(self.language_dir):
            return lang_dict

        for filename in os.listdir(self.language_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.language_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    # 获取语言名称
                    lang_name = data.get('meta', {}).get('name', 'Unknown')
                    lang_dict[lang_name] = file_path
                except Exception as e:
                    print(f"Error reading {filename}: {str(e)}")
        return lang_dict

    def reload_for_language(self, path: str):
        """切换语言并重新加载"""
        lang_code = os.path.basename(path).replace('.json', '')
        settings_manager.set_setting('window_language', lang_code)
        self.set_settings_path(self.get_current_lang_path())
        self._load_settings()

    def get_data(self):
        """仅获取UI中可动态修改部分"""
        return self.settings['data']

    def get_meta(self):
        return self.settings['meta']

    def get_static(self):
        return self.settings['static']

language_manager = LangManager()


class ConfigManager(JsonManage):
    def __init__(self):
        super().__init__()

        # 默认配置为空字典
        default_settings = {}
        self.set_default_settings(default_settings)

        # 配置文件路径
        config_dir = os.path.join(os.getcwd(), 'config')
        config_path = os.path.join(config_dir, 'configs.json')

        # 加载配置
        self.set_settings_path(config_path)

    def new_config(self, config_name, src_path, platform):
        """
        添加新的配置方案
        :param config_name: 配置方案名称
        :param src_path: 资源文件目标地址
        :param platform: 配置平台
        """
        # 创建配置信息字典
        config_info = {
            'resources_path':src_path,
            'time': self._get_current_time(),
            'platform': platform
        }

        # 添加或更新配置
        self.settings[config_name] = config_info
        self.save_settings()

    def remove_config(self, config_name):
        """
        删除配置方案
        :param config_name: 要删除的配置方案名称
        :return: 是否成功删除
        """
        if config_name in self.settings:
            del self.settings[config_name]
            self.save_settings()
            return True
        return False

    def get_config(self, config_name):
        """
        获取特定配置方案的信息
        :param config_name: 配置方案名称
        :return: 配置信息字典，如果不存在返回None
        """
        return self.settings.get(config_name)

    def get_all_configs(self):
        """
        获取所有配置方案
        :return: 所有配置方案的字典
        """
        return self.settings.copy()

    def update_config(self, config_name, group_path=None, platform=None):
        """
        更新现有配置方案
        :param config_name: 配置方案名称
        :param group_path: 新的配置组路径（可选）
        :param platform: 新的配置平台（可选）
        :return: 是否成功更新
        """
        if config_name not in self.settings:
            return False

        config_info = self.settings[config_name]
        if group_path:
            config_info['path'] = group_path
        if platform:
            config_info['platform'] = platform

        # 更新修改时间
        config_info['time'] = self._get_current_time()

        self.save_settings()
        return True

    @staticmethod
    def _get_current_time():
        """获取当前时间的字符串表示（ISO格式）"""
        from datetime import datetime
        return datetime.now().isoformat()

    def output_one_config(self, name, path):
        with open(os.path.join(path, 'configs.json'), 'w', encoding='utf-8') as f:
            config = self.get_config(name)
            config['name'] = name
            json.dump(config, f, ensure_ascii=False, indent=4)

    def input_one_config(self, path, new_name=None):
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if new_name:
                config['name'] = new_name
            name = config.pop('name')
            self.new_config(name, config['resources_path'], config['platform'])

config_manager = ConfigManager()


# 使用示例
if __name__ == "__main__":
    # 创建设置管理器

    # 获取设置
    print("当前窗口大小:", settings_manager.get_setting('window_size'))
    print("所有设置:", settings_manager.get_all_settings())


    # 获取配置信息
    print(config_manager.get_config("默认配置"))
    # 输出: {'配置组路径': '/path/to/config_group', '配置创建时间': '2023-10-15T14:30:00.123456', '配置平台': 'Windows'}

    # 更新配置
    config_manager.update_config("默认配置", group_path="/new/path", platform="Linux")

    # 获取所有配置
    all_configs = config_manager.get_all_configs()
    print(all_configs)

    # 删除配置
    config_manager.remove_config("默认配置")
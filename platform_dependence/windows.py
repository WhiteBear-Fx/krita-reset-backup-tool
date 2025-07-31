import json
import sys
import pywinstyles
import sv_ttk
import subprocess
import threading
import os
import json_manage
import shutil
import tkinter.messagebox as messagebox

# ======================= 公共API接口 =======================
def get_default_k_r_path():
    """
    获取Krita默认资源路径
    Get the default Krita resources path

    :return: Krita默认资源路径字符串 | Default Krita resources path string
    :rtype: str
    """
    return _get_default_k_r_path()


def get_app_icon():
    """
    获取应用程序图标路径
    Get the application icon path

    :return: 应用程序图标文件路径 | Application icon file path
    :rtype: str
    """
    return _get_app_icon()


def apply_theme_to_titlebar(master):
    """
    应用主题到窗口标题栏（Windows平台专用）
    Apply theme to window titlebar (Windows platform specific)

    :param master: Tkinter主窗口对象 | Tkinter main window object
    """
    _apply_theme_to_titlebar(master)


def set_krita_is_on_callback(callback):
    """
    设置Krita启动时的回调函数
    Set callback function when Krita starts

    :param callback: 回调函数 | Callback function
    """
    _set_krita_is_on_callback(callback)


def set_krita_is_off_callback(callback):
    """
    设置Krita关闭时的回调函数
    Set callback function when Krita stops

    :param callback: 回调函数 | Callback function
    """
    _set_krita_is_off_callback(callback)


def set_krita_is_unk_callback(callback):
    """
    设置Krita状态未知时的回调函数
    Set callback function when Krita status is unknown

    :param callback: 回调函数 | Callback function
    """
    _set_krita_is_unk_callback(callback)


def check_krita():
    """
    检查Krita是否正在运行
    Check if Krita is running

    :return: True表示正在运行, False表示未运行, None表示检查失败
             True if running, False if not, None if check failed
    :rtype: bool or None
    """
    return _check_krita()


def update_krita_status():
    """
    启动后台线程持续更新Krita状态，在状态更改时调用回调
    Start background thread to continuously update Krita status, call callback when state changes
    """
    _update_krita_status()


def new_krita_config(name):
    """
    创建新的Krita配置
    Create a new Krita configuration

    :param name: 配置名称 | Configuration name
    :return: (是否成功, 错误信息) | (Success status, Error message)
    :rtype: (bool, str or None)
    """
    return _new_krita_config(name)


def get_config_path(name):
    """
    获取配置自身的存储路径和内部记录的资源路径
    Obtain the storage path for configuring itself and the resource path for internal records

    :param name: 配置名称 | Configuration name
    :return: (存储路径, 资源路径) | (Storage path, Resources path)
    :rtype: (str, str)
    """
    return _get_config_path(name)


def check_configuration_path(name):
    """
    检查配置中的资源路径与目前程序设置的路径是否相同
    Check if the resource path in the configuration is the same as the path currently set in the program

    :param name: 配置名称 | Configuration name
    :return: 路径是否有效 | Whether the path is valid
    :rtype: bool
    """
    return _check_configuration_path(name)


def reset_krita():
    """
    重置Krita配置到初始状态
    Reset Krita configuration to initial state

    :return: 是否成功 | Whether succeeded
    :rtype: bool
    """
    return _reset_krita()


def use_krita_config(name):
    """
    应用指定的Krita配置
    Apply specified Krita configuration

    :param name: 配置名称 | Configuration name
    :return: 是否成功 | Whether succeeded
    :rtype: bool
    """
    return _use_krita_config(name)


def del_krita_config(name):
    """
    删除指定的Krita配置
    Delete specified Krita configuration

    :param name: 配置名称 | Configuration name
    :return: 是否成功 | Whether succeeded
    :rtype: bool
    """
    return _del_krita_config(name)


def output_krita_config(name, path):
    """
    导出Krita配置到ZIP文件
    Export Krita configuration to ZIP file

    :param name: 配置名称 | Configuration name
    :param path: 导出文件路径 | Export file path
    """
    _output_krita_config(name, path)


def extract_krita_config(path):
    """
    从ZIP文件提取Krita配置
    Extract Krita configuration from ZIP file

    :param path: ZIP文件路径 | ZIP file path
    :return: (资源路径, 平台, 名称, 临时路径) | (Resources path, Platform, Name, Temp path)
    :rtype: (str, str, str, str)
    """
    return _extract_krita_config(path)


def input_krita_config(path, new_name=None):
    """
    导入Krita配置
    Import Krita configuration

    :param path: 配置文件路径 | Configuration file path
    :param new_name: 可选的新名称 | Optional new name
    """
    _input_krita_config(path, new_name)


def get_platform_name():
    """
    获取当前平台名称
    Get current platform name

    :return: 平台名称 (如'windows') | Platform name (e.g. 'windows')
    :rtype: str
    """
    return _get_platform_name()

# ======================= 私有实现方法 =======================
_krita_local_appdata_path = [os.path.join(os.getenv('SYSTEMDRIVE'), os.getenv('LOCALAPPDATA'), 'krita.log'),
                             os.path.join(os.getenv('SYSTEMDRIVE'), os.getenv('LOCALAPPDATA'),'kritacrash.log'),
                             os.path.join(os.getenv('SYSTEMDRIVE'), os.getenv('LOCALAPPDATA'),'kritadisplayrc'),
                             os.path.join(os.getenv('SYSTEMDRIVE'), os.getenv('LOCALAPPDATA'),'kritarc'),
                             os.path.join(os.getenv('SYSTEMDRIVE'), os.getenv('LOCALAPPDATA'),'kritashortcutsrc'),
                             os.path.join(os.getenv('SYSTEMDRIVE'), os.getenv('LOCALAPPDATA'),'krita-sysinfo.log'), ]

def _get_default_k_r_path():
    default_k_r_path = os.path.join(os.getenv('APPDATA'), 'krita')
    return default_k_r_path

def _get_app_icon():
    return os.path.join(os.getcwd(), 'resources', 'app-icon.ico')

def _apply_theme_to_titlebar(master):
    """应用主题到Windows标题栏"""
    version = sys.getwindowsversion()

    # Windows 11特定处理
    if version.major == 10 and version.build >= 22000:
        # 根据当前主题设置标题栏颜色
        pywinstyles.change_header_color(master, "#1c1c1c" if sv_ttk.get_theme() == "dark" else "#fafafa")
        # 通过透明度微调强制刷新标题栏
        master.wm_attributes("-alpha", 0.99)
        master.wm_attributes("-alpha", 1)
    # Windows 10处理
    elif version.major == 10:
        pywinstyles.apply_style(master, "dark" if sv_ttk.get_theme() == "dark" else "normal")

_last_krita_status = None
_krita_is_on_callback = None
_krita_is_off_callback = None
_krita_is_unk_callback = None

def _set_krita_is_on_callback(callback):
    global _krita_is_on_callback
    _krita_is_on_callback = callback

def _set_krita_is_off_callback(callback):
    global _krita_is_off_callback
    _krita_is_off_callback = callback

def _set_krita_is_unk_callback(callback):
    global _krita_is_unk_callback
    _krita_is_unk_callback = callback

def _check_krita():
    try:
        # 检查krita.exe进程
        output = subprocess.check_output(
            ['tasklist', '/FI', 'IMAGENAME eq krita.exe'],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        is_run = b"krita.exe" in output

        return is_run
    except:
        # 出错时保持灰色状态
        # noinspection PyTypeChecker
        return None

def _update_krita_status():
    """后台更新Krita状态"""
    # noinspection PyBroadExceptio
    def _check():

        global _last_krita_status
        global _krita_is_on_callback
        global _krita_is_off_callback
        global _krita_is_unk_callback

        while True:
            is_running = _check_krita()
            if is_running is False and _last_krita_status != is_running:
                _last_krita_status = is_running
                if _krita_is_off_callback:
                    _krita_is_off_callback()

            elif is_running is True and _last_krita_status != is_running:
                _last_krita_status = is_running
                if _krita_is_on_callback:
                    _krita_is_on_callback()

            elif is_running is None and _last_krita_status != is_running:
                if _krita_is_unk_callback:
                    _krita_is_unk_callback()

            threading.Event().wait(0.5)

            # 启动后台线程
    threading.Thread(target=_check, daemon=True).start()

def _make_no_username_path(path: str):
    return path.replace(os.path.join(os.getenv('SYSTEMDRIVE'), os.getenv('HOMEPATH')), '{$USERDIR}')

def _add_username_path(path: str):
    return path.replace('{$USERDIR}',os.path.join(os.getenv('SYSTEMDRIVE'),os.getenv('HOMEPATH')))

def _new_krita_config(name):

    path = os.path.join('.', 'config', name)
    src_path = json_manage.settings_manager.get_setting('krita_resources_path').replace('/', '\\')
    src_path_no_username = _make_no_username_path(src_path)

    try:
        shutil.copytree(src_path, os.path.join(path, 'resources'))
        os.makedirs(os.path.join(path, 'config'))

        for i in _krita_local_appdata_path:
            try:
                shutil.copyfile(i, os.path.join(path, 'config', os.path.basename(i)))
            except FileNotFoundError:
                pass
        json_manage.config_manager.new_config(name, src_path_no_username, _get_platform_name())
        return True, None
    except Exception as e:
        messagebox.showerror(title=json_manage.language_manager.get_static().get('error'), message=str(e))
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
        return False, str(e)

def _get_path(name):
    path = os.path.join(os.getcwd(), 'config', name)
    sre_path = json_manage.config_manager.get_config(name).get('resources_path')
    return [path, sre_path]

def _get_config_path(name):
    path, sre_path = _get_path(name)
    return path, _add_username_path(sre_path)

def _check_configuration_path(name):
    path = _get_config_path(name)
    if path[1] != json_manage.settings_manager.get_setting('krita_resources_path'):
        return False
    return True

def _reset_krita():
    try:
        shutil.rmtree(json_manage.settings_manager.get_setting('krita_resources_path'))
        for i in _krita_local_appdata_path:
            try:
                os.remove(i)
            except FileNotFoundError:
                pass
            except Exception as e:
                messagebox.showerror(title=json_manage.language_manager.get_static().get('error'), message=str(e))
                return False
    except FileNotFoundError:
        return True

    except Exception as e:
        messagebox.showerror(title=json_manage.language_manager.get_static().get('error'),message=str(e))
        return False

    return True


def _use_krita_config(name):
    path, sre_path = _get_path(name)
    sre_path = _add_username_path(sre_path)

    try:
        _reset_krita()
        try:
            shutil.rmtree(_get_config_path(name)[1])
        except FileNotFoundError:
            pass

        try:
            shutil.copytree(os.path.join(path, 'resources'), sre_path)
        except Exception as e:
            messagebox.showerror(title=json_manage.language_manager.get_static().get('error'), message=str(e))
            return False


        for i in _krita_local_appdata_path:
            try:
                shutil.copyfile(os.path.join(path, 'config', os.path.basename(i)), i)
            except FileNotFoundError:
                pass
            except Exception as e:
                messagebox.showerror(title=json_manage.language_manager.get_static().get('error'), message=str(e))
                return False

    except FileNotFoundError:
        pass

    except Exception as e:
        messagebox.showerror(title=json_manage.language_manager.get_static().get('error'),message=str(e))
        return False
    if json_manage.settings_manager.get_setting('krita_resources_path') != sre_path:
        json_manage.settings_manager.set_setting('krita_resources_path', sre_path)
    return True

def _del_krita_config(name):
    path = _get_path(name)[0]
    try:
        shutil.rmtree(path)
        json_manage.config_manager.remove_config(name)
        return True
    except Exception as e:
        messagebox.showerror(title=json_manage.language_manager.get_static().get('error'), message=str(e))
        return False

def _output_krita_config(name, path):
    out_path = path.replace('/', '\\')
    path = _get_config_path(name)[0]
    temp_file_path = os.path.join(os.getcwd(),'temp', name)
    shutil.copytree(path, temp_file_path)
    json_manage.config_manager.output_one_config(name, temp_file_path)
    shutil.make_archive(out_path.replace('.zip', ''), 'zip', temp_file_path)
    shutil.rmtree(temp_file_path)

def _extract_krita_config(path):
    temp_file_path = os.path.join(os.getcwd(), 'temp', str(os.path.basename(path).replace('.zip', '')))
    shutil.unpack_archive(path, temp_file_path)
    try:
        with open(os.path.join(temp_file_path, 'configs.json'), 'r', encoding='utf-8') as f:
            configs = json.load(f)
            return _add_username_path(configs.get('resources_path')), configs.get('platform'), configs.get('name'), temp_file_path
    except Exception as e:
        messagebox.showerror(title=json_manage.language_manager.get_static().get('error'),message=str(e))

def _input_krita_config(path, new_name=None):
    json_manage.config_manager.input_one_config(os.path.join(path, 'configs.json'), new_name)
    shutil.copytree(os.path.join(path, 'resources'), os.path.join(os.getcwd(),'config', new_name, 'resources'))
    shutil.copytree(os.path.join(path, 'config'), os.path.join(os.getcwd(),'config', new_name, 'config'))

def _get_platform_name():
    return 'windows'
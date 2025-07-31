import sys

# 根据当前操作系统加载对应的平台模块
if sys.platform == 'win32':
    from .windows import *
else:
    from json_manage import language_manager
    raise OSError(language_manager.get_static().get('platform_unk'))
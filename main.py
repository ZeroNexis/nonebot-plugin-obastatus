import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

# 初始化 NoneBot
nonebot.init()
app = nonebot.get_asgi()

# 获取驱动器并注册适配器
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

# 加载内置插件和自定义插件
nonebot.load_builtin_plugins()
nonebot.load_plugins("nonebot_plugin_obastatus")

if __name__ == "__main__":
    nonebot.run(app="__main__:app")

from nonebot import get_plugin_config
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    oba_cookie: str  # 确保包含这个字段

    class Config:
        extra = "ignore"  # 忽略额外的配置字段
        env_file = ".env"

plugin_name = 'nonebot_plugin_obastatus'
plugin_version = 'v1.0.5'
plugin_config = get_plugin_config(Config)
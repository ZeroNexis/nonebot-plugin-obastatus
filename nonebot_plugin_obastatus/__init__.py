## 插件配置 部分
import nonebot
from .config import Config, plugin_name, plugin_version, plugin_config
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

## 机器人 部分
import json
import httpx
import locale
import asyncio
import aiofiles
import datetime
from loguru import logger
from random import choice
from nonebot.params import CommandArg
from nonebot import require, on_command, get_driver
from nonebot.adapters import Bot, Event, MessageSegment, Message

## 回复 & 发图 部分
require("nonebot_plugin_saa")
from nonebot_plugin_saa import Text, Image, MessageFactory

## 定时任务 部分
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

## 数据存储 部分
require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

# 插件初始化
driver = get_driver()

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_obastatus",
    description="获取 OpenBMCLAPI 相关数据",
    usage="""帮助: 返回帮助信息
总览: 返回 OpenBMCLAPI 当前状态
节点 <搜索条件>: 返回搜索到的节点信息
排名 <节点名次>: 返回指定名次的节点的详细信息
93HUB <(可选)图片搜索条件>: 相信你一定知道""",

    type="application",
    # 发布必填，当前有效类型有：`library`（为其他插件编写提供功能），`application`（向机器人用户提供功能）。

    homepage="https://github.com/Zero-Octagon/nonebot-plugin-obastatus",
    # 发布必填。

    config=Config,
    # 插件配置项类，如无需配置可不填写。

    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa")
    # 支持的适配器集合，其中 `~` 在此处代表前缀 `nonebot.adapters.`，其余适配器亦按此格式填写。
    # 若插件可以保证兼容所有适配器（即仅使用基本适配器功能）可不填写，否则应该列出插件支持的适配器。
)

cookie_headers = {
    "User-Agent": f"nonebot-plugin-obastatus/{plugin_version}",
    'Cookie': plugin_config.oba_cookie,
}

headers = {
    "User-Agent": f"nonebot-plugin-obastatus/{plugin_version}",
}

## 开机后先运行一遍重载缓存
@driver.on_startup
async def first_init_cache():
    await reload_cache()

# 存储单位格式化
def hum_convert(value):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size

# 数字分隔
def format_number(num):
    # 设置区域设置，以便使用逗号作为千位分隔符
    # 注意：这里假设您使用的是英文环境，如果是中文环境，可能需要使用'gbk环境'
    locale.setlocale(locale.LC_ALL, 'gbk')
    # 使用locale的格式化功能
    formatted = locale._format("%d", num, grouping=True)
    return formatted

# 按照名字搜索
def search_by_name(data, search_str, condition):
    # 初始化一个空列表来保存匹配的结果和它们的索引
    results_with_index = []
    
    # 遍历数据中的每一个项目，同时跟踪索引
    for index, item in enumerate(data):
        # 检查'item'字典中的'name'字段是否包含'search_str'
        if search_str.lower() in item.get(condition, '').lower():
            # 如果包含，将整个字典和它的索引添加到结果列表中
            results_with_index.append((index+1, item))
    
    # 返回所有匹配的项目及其索引
    return results_with_index

# 获取索引和对应内容
def get_record_by_index(records, index):
    if index < len(records) and index >= 0:
        return records[index]
    else:
        return None

# 读缓存
async def read_file_from_cache(filename: str):
    cache_file = store.get_cache_file(plugin_name, filename)
    async with aiofiles.open(cache_file, "r") as f:
        filelist_content = await f.read()
        filelist = json.loads(filelist_content)
    return filelist

# 写缓存
async def write_file_to_cache(filename, filelist):
    cache_file = store.get_cache_file(plugin_name, filename)
    async with aiofiles.open(cache_file, 'w') as f:
        await f.write(json.dumps(filelist))   

    logger.info(f"{filename} 的缓存保存成功")

# 刷新缓存
async def reload_cache():
    async with httpx.AsyncClient() as client:
        version = (await client.get('https://bd.bangbang93.com/openbmclapi/metric/version', headers=cookie_headers)).json()
        await write_file_to_cache('version.json', version)
        dashboard = (await client.get('https://bd.bangbang93.com/openbmclapi/metric/dashboard', headers=cookie_headers)).json()
        await write_file_to_cache('dashboard.json', dashboard)
        rank = (await client.get('https://bd.bangbang93.com/openbmclapi/metric/rank', headers=cookie_headers)).json()
        await write_file_to_cache('rank.json', rank)

scheduler.add_job(
    reload_cache, "interval", minutes=1, id="timed_cache_refresh"
)

# 插件的帮助面板
help = on_command("帮助")
@help.handle()
async def handle_function(bot: Bot):
    help_msg = f'''OpenBMCLAPI 面板数据 {plugin_version}
帮助: 返回此信息
总览: 返回 OpenBMCLAPI 当前状态
节点 <搜索条件>: 返回搜索到的节点信息
排名 <节点名次>: 返回指定名次的节点的详细信息
93HUB <(可选)图片搜索条件>: 相信你一定知道
Tips: 结果 >3 条显示部分信息，结果 > 10条不显示任何信息（搜索可爱除外）
特别鸣谢: 盐木、甜木、米露、听风、天秀 和 bangbang93 的不杀之恩
'''
    await MessageFactory(help_msg).finish(reply=True)
    
# OpenBMCLAPI 总览
status = on_command("总览")
@status.handle()
async def handle_function(bot: Bot, event: Event):
    version = await read_file_from_cache('version.json')
    dashboard = await read_file_from_cache('dashboard.json')
    status_msg = f'''OpenBMCLAPI 面板数据 {plugin_version}
官方版本: {version.get('version')} | 提交ID: {version.get('_resolved').split('#')[1][:7]}
在线节点数: {dashboard.get('currentNodes')} 个 | 负载: {round(dashboard.get('load')*100, 2)}%
总带宽: {dashboard.get('bandwidth')} Mbps | 出网带宽: {round(dashboard.get('currentBandwidth'), 2)} Mbps
当日请求: {format_number(dashboard.get('hits'))} 次 | 数据量: {hum_convert(dashboard.get('bytes'))}
请求时间: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
数据源: https://bd.bangbang93.com/pages/dashboard'''
    await MessageFactory(status_msg).finish(reply=True)

# 根据 节点名称 搜索节点详细信息   
node = on_command("节点")
@node.handle()
async def handle_function(bot: Bot, event: Event, args: Message = CommandArg()):
    args = str(args).replace('\n', '')
    send_text = f'OpenBMCLAPI 面板数据 {plugin_version}'
    if str(args) == '' or str(args).isspace():
        send_text += '\n缺参数啦！记得补上喵喵～'
    elif len(str(args)) > 16:
        send_text += '''\n要求: 节点名称 最多 16 个字符
搜索条件不符合要求，请调整参数后重新尝试'''
    else:
        rank = await read_file_from_cache('rank.json')
        version = await read_file_from_cache('version.json')
        matches_with_index = search_by_name(rank, str(args), 'name')
        if len(matches_with_index) > 0 and len(matches_with_index) <= 3:
            for index, match in matches_with_index:
                enabled_status = '❔'
                fullSize_status = '❔'
                version_status = '❔'
                # 节点状态检测
                if match.get('isEnabled'):
                    enabled_status = '✅'
                else:
                    enabled_status = '❌'
                # 节点类型检测
                if match.get('fullSize'):
                    fullSize_status = '🌕'
                else:
                    fullSize_status = '🌗'
                # 节点版本检测
                if match.get('version') is not None:
                    if match.get('version') == version.get('version'):
                        version_status = '🟢'
                    else:
                        version_status = '🟠'

                send_text += f'''\n{enabled_status}{fullSize_status} | {index} | {match.get('name')} | {match.get('version', '未知')}{version_status}
所有者: {match.get('user', {}).get('name', '未知')} | 赞助商: {match.get('sponsor', {}).get('name', '未知')}
当日流量: {hum_convert(match.get('metric', {}).get('bytes', 0))} | 当日请求数: {format_number(match.get('metric', {}).get('hits', 0))} 次'''
        elif (len(matches_with_index) > 3 and len(matches_with_index) <= 10) or str(args) == '可爱':
            for index, match in matches_with_index:
                # 节点状态检测
                if match.get('isEnabled') == True:
                    enabled_status = '✅'
                else:
                    enabled_status = '❌'
                send_text += f'''\n{enabled_status} | {index} | {match.get('name')} | {hum_convert(match.get('metric', {}).get('bytes', 0))} | {format_number(match.get('metric', {}).get('hits', 0))}'''
        elif len(matches_with_index) > 10 and str(args) != '可爱':
            send_text += f'\n搜索到{len(matches_with_index)}个节点，请改用更精确的名字'
        else:
            send_text += f'\n未找到有关 {args} 的相关节点信息，请调整参数后重新尝试'
    send_text += f'\n请求时间: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    await MessageFactory(send_text).finish(reply=True)

# 根据 节点ID 搜索拥有者
node_id= on_command("ID")
@node_id.handle()
async def handle_function(bot: Bot, event: Event, args: Message = CommandArg()):
    args = str(args).replace('\n', '')
    send_text = f'OpenBMCLAPI 面板数据 {plugin_version}'
    if str(args) == '' or str(args).isspace():
        send_text += '\n缺参数啦！记得补上喵喵～'
    elif len(str(args)) > 24:
        send_text += f'''\n要求: 节点ID 最多 24 个字符
搜索条件不符合要求，请调整参数后重新尝试'''
    else:
        rank = await read_file_from_cache('rank.json')
        version = await read_file_from_cache('dashboard.json')
        matches_with_index = search_by_name(rank, str(args), '_id')
        if len(matches_with_index) > 0 and len(matches_with_index) <= 3:
            for index, match in matches_with_index:
                enabled_status = '❔'
                fullSize_status = '❔'
                version_status = '❔'
                # 节点状态检测
                if match.get('isEnabled'):
                    enabled_status = '✅'
                else:
                    enabled_status = '❌'
                # 节点类型检测
                if match.get('fullSize'):
                    fullSize_status = '🌕'
                else:
                    fullSize_status = '🌗'
                # 节点版本检测
                if match.get('version') is not None:
                    if match.get('version') == version.get('version'):
                        version_status = '🟢'
                    else:
                        version_status = '🟠'
            send_text += f'''\n{enabled_status}{fullSize_status} | {index} | {match.get('name')} | {match.get('version', '未知')}{version_status}
所有者: {match.get('user', {}).get('name', '未知')} | 赞助商: {match.get('sponsor', {}).get('name', '未知')}
当日流量: {hum_convert(match.get('metric', {}).get('bytes', 0))}
当日请求数: {format_number(match.get('metric', {}).get('hits', 0))} 次
ID: {match.get('_id')}'''
        elif len(matches_with_index) > 3 and len(matches_with_index) <= 10:
            for index, match in matches_with_index:
                # 节点状态检测
                enabled_status = '❔'
                fullSize_status = '❔'
                version_status = '❔'
                if match.get('isEnabled') == True:
                    enabled_status = '✅'
                else:
                    enabled_status = '❌'
                # 节点类型检测
                if match.get('fullSize') == True:
                    fullSize_status = '🌕'
                else:
                    fullSize_status = '🌗'
                # 节点版本检测
                if match.get('version') != None:
                    if match.get('version') == version.get('version'):
                        version_status = '🟢'
                    else:
                        version_status = '🟠'
                send_text += f'''\n{enabled_status}{fullSize_status}{version_status} | {index} | {match.get('name')} | {hum_convert(match.get('metric', {}).get('bytes', 0))} | {format_number(match.get('metric', {}).get('hits', 0))}'''

        elif len(matches_with_index) > 10:
            send_text += f'''\n搜索到{len(matches_with_index)}个节点，请改用更精确的ID
请求时间: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'''
        else:
            send_text += f'\n未找到有关 {args} 的相关节点信息，请调整参数后重新尝试'
    send_text += f'\n请求时间: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    await MessageFactory(send_text).finish(reply=True)
            
# 根据 节点名称 搜索节点详细信息   
node_rank = on_command("排名")
@node_rank.handle()
async def handle_function(bot: Bot, event: Event, args: Message = CommandArg()):
    args = str(args).replace('\n', '')
    send_text = f'OpenBMCLAPI 面板数据 {plugin_version}'
    rank = await read_file_from_cache('rank.json')
    version = await read_file_from_cache('version.json')
    try:
        index = int(str(args))-1
        match = get_record_by_index(rank, index)
        if match is not None:  # 正常情况
            enabled_status = '❔'
            fullSize_status = '❔'
            version_status = '❔'
            # 节点状态检测
            if match.get('isEnabled'):
                enabled_status = '✅'
            else:
                enabled_status = '❌'
            # 节点类型检测
            if match.get('fullSize'):
                fullSize_status = '🌕'
            else:
                fullSize_status = '🌗'
            # 节点版本检测
            if match.get('version') is not None:
                if match.get('version') == version.get('version'):
                    version_status = '🟢'
                else:
                    version_status = '🟠'
            send_text += f'''\n{enabled_status}{fullSize_status} | {index+1} | {match.get('name')} | {match.get('version', '未知')}{version_status}
所有者: {match.get('user', {}).get('name', '未知')} | 赞助商: {match.get('sponsor', {}).get('name', '未知')}
当日流量: {hum_convert(match.get('metric', {}).get('bytes', 0))}
当日请求数: {format_number(match.get('metric', {}).get('hits', 0))} 次'''
            send_text += f'\n请求时间: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        else:   # 超了
            send_text += f'\n索引超出范围，请输入一个有效的数字。'
    except ValueError:
        if str(args) == '' or str(args).isspace():
            send_text += '\n缺参数啦！记得补上喵喵～'
        else:
            send_text +=  f'''\n要求: 节点名次 必须为一个整数
搜索条件不符合要求，请调整参数后重新尝试'''
    send_text += f'\n请求时间: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    await MessageFactory(send_text).finish(reply=True)
            
# 随机获取 Mxmilu666/bangbang93HUB 中精华图片
bangbang93HUB = on_command("93HUB")
@bangbang93HUB.handle()
async def handle_function(bot: Bot, event: Event, args: Message = CommandArg()):
    args = str(args).replace('\n', '')
    if str(args) == '' or str(args).isspace():
        send_text = Image('https://apis.bmclapi.online/api/93/random')
    else:
        matchList = []
        imageList = httpx.get('https://ttb-network.top:8800/mirrors/bangbang93hub/filelist', headers=headers).json()

        for i in imageList:
            if str(args).lower() in i:
                matchList.append(i)

        if len(matchList) < 1:
            send_text = '找不到哦，请重新尝试~'
        elif len(matchList) == 1:
            send_text = Image(f'https://apis.bmclapi.online/api/93/file?name={matchList[0]}')
        else:
            send_text = f'搜索结果包含 {len(matchList)} 条，请改用更加精确的参数搜索'
    await MessageFactory(send_text).finish(reply=True)
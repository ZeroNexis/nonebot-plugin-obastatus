<div align="center">
  <a href="https://nonebot.dev/store/plugins"><img src="https://jsd.onmicrosoft.cn/gh/A-kirami/nonebot-plugin-obastatus@resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://jsd.onmicrosoft.cn/gh/A-kirami/nonebot-plugin-obastatus@resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot_plugin_obastatus

_✨ 获取 OpenBMCLAPI 相关数据 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/Zero-Octagon/nonebot-plugin-obastatus.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-obastatus">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-obastatus.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

## 📖 介绍

基于 [nonebot2](https://github.com/nonebot/nonebot2) 和 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 的 OpenBMCLAPI 相关数据查询插件

## 💿 安装

- 使用 nb-cli 安装
```shell
nb plugin install nonebot-plugin-obastatus
```

- 使用包管理器安装
```shell
pip install nonebot-plugin-obastatus
```

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的相关配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| OBA_COOKIE | 是 | 无 | 获取数据时必需的参数，未填写则会出现问题 |

## 🎉 使用
### 指令表
**使用前请先确保命令前缀为空，否则请在以下命令前加上命令前缀。**
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 帮助 | 无 | 否 | 全部 | 返回帮助信息 |
| 总览 | 无 | 否 | 全部 | 返回 OpenBMCLAPI 当前状态 |
| 节点 <搜索条件> | 无 | 否 | 全部 | 返回搜索到的节点信息 |
| 排名 <节点名次> | 无 | 否 | 全部 | 返回指定名次的节点的详细信息 |
| 93HUB <(可选)图片搜索条件> | 无 | 否 | 全部 | 相信你一定知道 |

### 效果图
尚未进行测试，请耐心等待开发组进行测试。

## 💡 特别鸣谢

**shenjack**
- [rua！](https://github.com/shenjackyuanjie/icalingua-python-bot) - 给予创建项目的灵感

**@bangbang93**
- [OpenBMCLAPI](https://qm.qq.com/q/2OfvVrAwVG) - 使用其API完成该项目中过半的内容


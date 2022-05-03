from loguru import logger
from nonebot import get_driver, on_message, on_notice, on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, MessageEvent, GroupMessageEvent, Message, PokeNotifyEvent
from nonebot.params import CommandArg, State
from pathlib import Path
import random
import httpx
import re
import os

from typing import Dict, List
from nonebot.rule import Rule
from nonebot_plugin_manager import PluginManager
from ..help.plugin import get_plugins


driver = get_driver()
dir_path = Path(__file__).parent
resource_path = dir_path / "resource"
runtime_data = {}



def manager_rule(bot: Bot, event: MessageEvent) -> bool:
    return isinstance(event, GroupMessageEvent) and (
        str(event.user_id) in bot.config.superusers
        or event.sender.role in ["admin", "owner"]
    )
block = on_command("block", aliases={"禁用"}, block=True)
unblock = on_command("unblock", aliases={"启用"}, block=True)
chmod = on_command("chmod", block=True)

Conv = Dict[str, List[int]]


def get_conv(event: MessageEvent) -> Conv:
    return {
        "user": [event.user_id],
        "group": [event.group_id] if isinstance(event, GroupMessageEvent) else [],
    }


@block.handle()
async def _(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        return

    plugins = get_plugins(event)
    plugin = None
    for p in plugins[::-1]:
        if keyword.lower() in (p.name.lower(), p.short_name.lower()):
            plugin = p
            break
    if not plugin:
        await block.finish(f"没有 {keyword}")

    plugin_manager = PluginManager()
    conv: Conv = get_conv(event)
    if conv["group"]:
        conv["user"] = []
    result = plugin_manager.block_plugin([plugin.name], conv)
    if result.get(plugin.name, False):
        res = f"{plugin.short_name or plugin.name}"
    # else:
    #     res = f"插件 {plugin.short_name or plugin.name} 不存在或已关闭编辑权限！"
    img_path = "file:///" + str(resource_path / "atrino.jpg")
    await block.finish(MessageSegment.text(res) + MessageSegment.image(img_path))


@unblock.handle()
async def _(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        return

    plugins = get_plugins(event)
    plugin = None
    for p in plugins[::-1]:
        if keyword.lower() in (p.name.lower(), p.short_name.lower()):
            plugin = p
            break
    if not plugin:
        await unblock.finish(f"没有 {keyword}")

    plugin_manager = PluginManager()
    conv: Conv = get_conv(event)
    if conv["group"]:
        conv["user"] = []
    if plugin.name == "setu" and not str(event.user_id) in bot.config.superusers:
        img_path = "file:///" + str(resource_path / "notsese.gif")
        await unblock.finish(MessageSegment.image(img_path))
    result = plugin_manager.unblock_plugin([plugin.name], conv)
    if result.get(plugin.name, False):
        res = f"{plugin.short_name or plugin.name}"
    # else:
    #     res = f"插件 {plugin.short_name or plugin.name} 不存在或已关闭编辑权限！"
    img_path = "file:///" + str(resource_path / "atriyes.jpg")
    await unblock.finish(MessageSegment.text(res) + MessageSegment.image(img_path))

@chmod.handle()
async def _(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        return
    param = keyword.split()
    mode = param[0]
    plugin_name = param[1]
    gid = param[2]
    if gid == None and isinstance(event, GroupMessageEvent):
        gid = event.group_id
    logger.info(param)
    logger.info(mode)
    logger.info(plugin_name)
    logger.info(gid)
    #chmod 7 pluginname groupoid
    plugin_list = []
    plugins = get_plugins(event)
    if plugin_name == "all":
        for p in plugins[::-1]:
            plugin_list.append(p.name)
    else:
        plugin = None
        for p in plugins[::-1]:
            if plugin_name.lower() in (p.name.lower(), p.short_name.lower()):
                # plugin = p
                plugin_list.append(p.name)
                break
        if not plugin:
            await unblock.finish(f"没有 {plugin_name}")

    plugin_manager = PluginManager()
    conv: Conv = get_conv(event)
    if conv["group"]:
        conv["user"] = []
    result = plugin_manager.group_chmod(plugin_list, conv, int(mode))
    # res = ""
    # if result.get(plugin.name, False):
    #     res = f"{plugin.short_name or plugin.name}"
    await unblock.finish(MessageSegment.text(str(event.message) + " succ"))
    
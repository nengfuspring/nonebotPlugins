from typing import Optional, Union
from nonebot import on_command, get_driver
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    GroupMessageEvent,
    Message,
    MessageSegment,
)

from .data_source import get_help_img, get_plugin_img
from .plugin import get_plugins
from .browser import shutdown_browser



driver = get_driver()
help = on_command("help", aliases={"帮助", "功能"}, block=True)

@driver.on_startup
async def on_botstart():
    await shutdown_browser()
@driver.on_shutdown
async def on_botshutdown():
    await shutdown_browser()

@help.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    plugin_name = msg.extract_plain_text().strip()

    help_msg = None
    if plugin_name:
        help_msg = await get_help_msg(event, plugin_name)
    elif event.is_tome():
        help_msg = await get_help_msg(event)
    if help_msg:
        await help.finish(help_msg)


async def get_help_msg(
    event: MessageEvent, plugin_name: str = ""
) -> Optional[Union[str, MessageSegment]]:
    plugins = get_plugins(event)
    if not plugin_name:
        if not plugins:
            return "暂时没有可用的功能"
        event_type = "group" if isinstance(event, GroupMessageEvent) else "private"
        img = await get_help_img(event_type, plugins)
        return MessageSegment.image(img) if img else "出错了，请稍后再试"
    else:
        for p in plugins:
            if plugin_name.lower() in (p.name.lower(), p.short_name.lower()):
                img = await get_plugin_img(p)
                return MessageSegment.image(img) if img else "出错了，请稍后再试"
        return None

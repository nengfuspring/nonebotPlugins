import asyncio
import traceback
from typing import List, Dict
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler, T_State
from nonebot.message import event_postprocessor
from nonebot.params import EventMessage, CommandArg
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent, MessageSegment
from nonebot.log import logger

from .data_source import sources, Source, download_image
from .config import hikari_config


__help__plugin_name__ = "imgSearch"
__des__ = "搜图"
__cmd__ = "搜图[图片]"
__short_cmd__ = __cmd__
__example__ = " "
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"


last_img: Dict[str, str] = {}


def get_cid(event: MessageEvent):
    return (
        f"group_{event.group_id}"
        if isinstance(event, GroupMessageEvent)
        else f"private_{event.user_id}"
    )


@event_postprocessor
async def save_last_img(event: MessageEvent, msg: Message = EventMessage()):
    cid = get_cid(event)
    if imgs := msg["image"]:
        last_img.update({cid: imgs[-1].data["url"]})


def get_img_url(
    event: MessageEvent,
    state: T_State,
    msg: Message = EventMessage(),
    arg: Message = CommandArg(),
) -> bool:
    img_url = ""
    if event.reply:
        if imgs := event.reply.message["image"]:
            img_url = imgs[0].data["url"]
    elif imgs := msg["image"]:
        img_url = imgs[0].data["url"]
    if not img_url:
        if arg.extract_plain_text().strip().startswith("上一张"):
            cid = get_cid(event)
            img_url = last_img.get(cid, "")
    if img_url:
        state["img_url"] = img_url
        return True
    return False


def create_matchers():
    def create_handler(source: Source) -> T_Handler:
        async def handler(
            bot: Bot, matcher: Matcher, event: MessageEvent, state: T_State
        ):
            img_url: str = state["img_url"]
            try:
                img = await download_image(img_url)
            except:
                logger.warning(traceback.format_exc())
                # await matcher.finish("图片下载出错，请稍后再试")
            res = None
            try:
                res = await source.func(img)
            except:
                logger.warning(traceback.format_exc())
                # await matcher.finish("出错了，请稍后再试")

            help_msg = ""#f"当前搜索引擎：{source.name}\n可使用 {options} 命令使用其他引擎搜索"
            if res:
                await send_msg(
                    bot,
                    matcher,
                    event,
                    res[: hikari_config.hikarisearch_max_results],
                    help_msg,
                )
            else:
                # await matcher.finish(f"{source.name} 中未找到匹配的图片")
                await matcher.finish("出错了，请稍后再试")

        return handler

    for source in sources:
        on_command(
            source.commands[0],
            get_img_url,
            aliases=set(source.commands),
            block=True,
            priority=13,
        ).append_handler(create_handler(source))


create_matchers()


async def send_msg(
    bot: Bot, matcher: Matcher, event: MessageEvent, msgs: List[Message], help_msg: str
):
    if isinstance(event, GroupMessageEvent) and len(msgs) > 1:
        # msgs.insert(0, Message(help_msg))
        info = await bot.get_group_member_info(group_id=int(event.group_id), user_id=int(bot.self_id))
        name = info.get("card", "") or info.get("nickname", "")
        await send_forward_msg(bot, event, name, bot.self_id, msgs)
    else:
        for msg in msgs:
            await matcher.send(msg)
            await asyncio.sleep(2)


async def send_forward_msg(
    bot: Bot,
    event: GroupMessageEvent,
    name: str,
    uin: str,
    msgs: List[Message],
):
    def to_json(msg: Message):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    # await bot.send(event, messages)
    # logger.info(messages)
    try:
        await bot.send_group_forward_msg(group_id=event.group_id, messages=messages)
    except Exception as e:
        logger.info(e)
        await bot.send(event, "出错了", at_sender = True)

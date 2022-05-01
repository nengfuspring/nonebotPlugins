from nonebot import get_driver, on_command, logger
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, MessageEvent, GroupMessageEvent, Message
from nonebot.params import CommandArg
from pathlib import Path
import urllib.request
import hashlib
import re
import httpx
import imghdr

__help__plugin_name__ = "bigger"
__des__ = "图片变大"
__cmd__ = "变大[图片]"
__short_cmd__ = __cmd__
__example__ = "变大[图片]"
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"

driver = get_driver()
dir_path = Path(__file__).parent
resource_path = dir_path / "resource"
runtime_data = {}


bigger = on_command("变大", priority=6, block=True)
@bigger.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    gid = str(event.group_id)
    meta = getPicMeta(str(event.message))
    imgPath = meta[0]
    md5 = str(meta[1]).split(".")[0]

    img = httpx.get(imgPath)
    tempImgPath = resource_path / "bianda.gif"
    urllib.request.urlretrieve(imgPath, tempImgPath)
    # with open(tempImgPath, 'rb') as fp:
    #     data = fp.read()
    # md5 = hashlib.md5(data).hexdigest() + ""
    imgType = imghdr.what(tempImgPath)

    logger.info(md5)
    logger.info(imgType)
    if (imgType == 'gif' or imgType == "GIF") and not str(event.user_id) in bot.config.superusers:
        await bigger.finish(MessageSegment.text("不支持动图"), at_sender = True)
    post = "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID=\"5\" templateID=\"1\" action=\"\" brief=\"&#91;表情图片&#93;\" sourceMsgId=\"0\" url=\"\" flag=\"0\" adverSign=\"0\" multiMsgFlag=\"0\"><item layout=\"0\" advertiser_id=\"0\" aid=\"0\"><image uuid=\"" + md5 + ".gif\" md5=\""+ md5 +"\" GroupFiledid=\"3070374325\" minWidth=\"400\" minHeight=\"400\" maxWidth=\"400\" maxHeight=\"400\" /></item><source name=\"\" icon=\"\" action=\"\" appid=\"-1\" /></msg>"
    post = "<?xml version='1.0' encoding='utf-8' standalone='yes' ?><msg serviceID='5' templateID='1' brief='[表情图片]' ><item layout=\"0\" advertiser_id=\"0\" aid=\"0\"><image uuid='"+ md5 +".jpg' md5='"+ md5 +"' GroupFiledid='2386948994' minWidth='400' minHeight='400' maxWidth='400' maxHeight='400'/></item><source name='' icon='' appid='-1' action='' i_actionData='' a_actionData='' url=''/></msg>"
    post = "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID='5' templateID='1' action='' brief='[表情图片]' sourceMsgId='0' url='' flag='0' adverSign='0' multiMsgFlag='0'><item layout='0' advertiser_id='0' aid='0'><image uuid='"+ md5 +".jpg' md5='"+ md5 +"' GroupFiledid='0' filesize='36951' local_path='' minWidth='400' minHeight='400' maxWidth='400' maxHeight='400' /></item><source name='' icon='' action='' appid='-1' /></msg>"
    logger.info(imgPath)
    try:
        await bigger.send(MessageSegment.image(imgPath) + MessageSegment.xml(post))
    except:
        await bigger.send(MessageSegment.text("出错了"), at_sender = True)


def getPicMeta(message: str):
    return re.findall("url=(.*?)[,|\]]", message)[0], re.findall("file=(.*?)[,|\]]", message)[0]
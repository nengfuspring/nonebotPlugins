from nonebot import get_driver, on_command, require
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, MessageEvent, GroupMessageEvent, Message
from nonebot.params import CommandArg
from pathlib import Path
import httpx
import json
import nonebot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = require("nonebot_plugin_apscheduler").scheduler


__help__plugin_name__ = "bing"
__des__ = "bing每日一图"
__cmd__ = "bing"
__short_cmd__ = __cmd__
__example__ = "bing"
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"

driver = get_driver()
dir_path = Path(__file__).parent
resource_path = dir_path / "resource"
bing_runtime_data = {}

@driver.on_startup
async def on_botstart():
    print("on_botstart")
    global bing_runtime_data
    try:
        with open(dir_path / "db_record.json", "r", encoding="utf-8") as f:
            bing_runtime_data = json.load(f)
            f.close()
            if bing_runtime_data == None:
                bing_runtime_data = {}
    except:
        bing_runtime_data = {}
    scheduler.add_job(bing_wall_paper, "cron", hour=8, minute=0, id=str(1))

bing = on_command("bing", priority=6, block=True)
@bing.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    response = httpx.get("https://bing.biturl.top/")
    jsonStr = json.load(response)
    img = httpx.get(jsonStr.get("url"))
    await bing.send(MessageSegment.text("bing每日一图\n" + jsonStr.get("copyright")) + MessageSegment.image(img.content))

subscribe = on_command("订阅bing",aliases={"取消bing"}, priority=6, block=True)
@subscribe.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    global bing_runtime_data
    gid = str(event.group_id)
    commd_val = "订阅" in str(event.message)
    if bing_runtime_data.get("subscribe") == None:
        bing_runtime_data["subscribe"] = []
    subscribed = False
    for subscribe_id in bing_runtime_data.get("subscribe"):
        if subscribe_id == gid:
            subscribed = True
    if commd_val and not subscribed:
        bing_runtime_data.get("subscribe").append(gid)
    if not commd_val and subscribed:
        bing_runtime_data.get("subscribe").remove(gid)
    dbsave()
    await subscribe.send(MessageSegment.at(event.user_id) + MessageSegment.text(str(event.message) + " 成功~"))
    
async def bing_wall_paper():
    response = httpx.get("https://bing.biturl.top/")
    jsonStr = json.load(response)
    img = httpx.get(jsonStr.get("url"))
    # tempImgPath = project_path + "resource/img/temp/bing.jpg"
    # urllib.request.urlretrieve(jsonStr.get("url"), tempImgPath)
    # with open(tempImgPath, 'rb') as fp:
    #     data = fp.read()
    # md5 = hashlib.md5(data).hexdigest() + ""
    # post = "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID='5' templateID='1' action='' brief='[bing每日一图]' sourceMsgId='0' url='' flag='0' adverSign='0' multiMsgFlag='0'><item layout='0' advertiser_id='0' aid='0'><image uuid='"+ md5 +".jpg' md5='"+ md5 +"' GroupFiledid='0' filesize='36951' local_path='' minWidth='400' minHeight='400' maxWidth='400' maxHeight='400' /></item><source name='' icon='' action='' appid='-1' /></msg>"
    
    # await nonebot.get_bot().send_group_msg(group_id=757287826, message = MessageSegment.text("bing每日一图\n" + jsonStr.get("copyright")))
    # await nonebot.get_bot().send_group_msg(group_id=757287826, message = MessageSegment.image(img.content) + MessageSegment.xml(post))
    # if cmdgid != None:
    #     await nonebot.get_bot().send_group_msg(group_id=cmdgid, message = MessageSegment.text("bing每日一图\n" + jsonStr.get("copyright")) + MessageSegment.image(img.content))
    # else:
    if bing_runtime_data.get("subscribe") == None:
        bing_runtime_data["subscribe"] = []
    for gid in bing_runtime_data["subscribe"]:
        await nonebot.get_bot().send_group_msg(group_id=gid, message = MessageSegment.text("bing每日一图\n" + jsonStr.get("copyright")) + MessageSegment.image(img.content))
    # await m.send(MessageSegment.text(jsonStr.get("copyright")) + MessageSegment.image(img.content))

def dbsave():
    global bing_runtime_data
    print(bing_runtime_data)
    with open(dir_path / "db_record.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(bing_runtime_data))
        f.close()
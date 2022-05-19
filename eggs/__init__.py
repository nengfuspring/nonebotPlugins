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


__help__plugin_name__ = "eggs"
__des__ = "一些彩蛋"
__cmd__ = " "
__short_cmd__ = __cmd__
__example__ = " "
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"

driver = get_driver()
dir_path = Path(__file__).parent
resource_path = dir_path / "resource"
runtime_data = {}

async def _group_poke(event: PokeNotifyEvent) -> bool:
        return event.is_tome()
group_poke = on_notice(_group_poke, priority=10, block=True)
@group_poke.handle()
async def pokefuc(bot: Bot, event: PokeNotifyEvent, state: T_State = State()):
    print("grouppokeEvent")
    await group_poke.send(MessageSegment.text("打咩"))


egg = on_message(priority=2, block=False)
@egg.handle()
# async def _(bot: Bot, event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
async def _(bot: Bot, event: GroupMessageEvent, state: T_State = State()):
    gid = str(event.group_id)
    print(str(event.message))
    if str(event.message) == "我会自己上厕所":
        print("file:///" + str(resource_path / "shangcesuo_01.mp3"))
        await egg.send(MessageSegment.record( "file:///" + str(resource_path / "shangcesuo_01.mp3")))
    
    if "CQ:image" in str(event.message):
        meta = getPicMeta(str(event.message))
        print(meta[1])
        if meta[1] == "acf2533853ee9f75e8e18a4d95d23a06.image" or meta[1] == "b1e2e0216b8b591fb5ddeb7c2f0e8db0.image":
            await egg.send(MessageSegment.image("file:///" + str(resource_path / "atrileft.png")))
        if meta[1] == "73e23c3a2723753abd93d3117af6c0e0.image" or meta[1] == "02b939b62b9db6fad706af92bff56506.image":
            await egg.send(MessageSegment.image("file:///" + str(resource_path / "atriright.png")))


    if str(event.message) == "猫猫":
        # api = "https://random.dog/"
        img = httpx.get("http://edgecats.net/")
        await egg.send(MessageSegment.image(img.content))

    if "老婆" in str(event.message) and event.to_me:
        if random.randint(0, 100) > 30:
            await egg.send(MessageSegment.at(event.user_id) + MessageSegment.text("老婆"))
        else:
            await egg.send(MessageSegment.at(event.user_id) + MessageSegment.text("郭楠收收味"))

    if "随机吉卜力11" in str(event.message):
        msgStr = str(event.message)
        count = 1
        isOverflow = False
        if len(msgStr) > 5:
            try:
                count = int(str(event.message)[5:len(str(event.message))])
            except Exception:
                print("随机吉普力err")
        if count > 5 :
            count = 5
            isOverflow = True
        index = 0
        if isOverflow :
            # imgMsg += MessageSegment.text("最多要5张哦")
            await egg.send(MessageSegment.text("最多要5张哦"))
        while index < count :
            imgPath = getGroupRandomFile(gid, "ghibliImg", f"{resource_path}/img/ghibli")
            path = f"file:///{imgPath}"
            index += 1
            # imgMsg += MessageSegment.image(path)
            await egg.send(MessageSegment.image(path))

    if str(event.message) == "atrii":
        # voicePath = getGroupRandomFile(gid, "atriVoice", f"{project_path}resource\\voice")
        # path = f"file:///{voicePath}"
        # await m.send(MessageSegment.record(path))
        # member_list = await bot.get_friend_list()
        # print(member_list)
        # res = throw()
        # if isinstance(res, str):
        #     await m.finish(res)
        # else:
        #     await m.finish(MessageSegment.image(res))
        post = "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID=\"5\" templateID=\"1\" action=\"\" brief=\"&#91;图片表情&#93;\" sourceMsgId=\"0\" url=\"\" flag=\"0\" adverSign=\"0\" multiMsgFlag=\"0\"><item layout=\"0\" advertiser_id=\"0\" aid=\"0\"><image uuid=\"81CD9987C65701ABC08560E761B24CFC.gif\" md5=\"81CD9987C65701ABC08560E761B24CFC\" GroupFiledid=\"3032610211\" filesize=\"218138\" local_path=\"/storage/emulated/0/Android/data/com.tencent.mobileqq/Tencent/MobileQQ/chatpic/chatimg/aa3/Cache_10ade3c8fe5d5aa3\" minWidth=\"400\" minHeight=\"400\" maxWidth=\"400\" maxHeight=\"400\" /></item><source name=\"\" icon=\"\" action=\"\" appid=\"-1\" /></msg>"
        # await m.send(MessageSegment.xml(post))
    if "老几" in str(event.message) and "安排了" in str(event.message) and gid == "596451786":
        await egg.send(MessageSegment.at(1539826729))
    
def getPicMeta(message: str):
    return re.findall("url=(.*?)[,|\]]", message)[0], re.findall("file=(.*?)[,|\]]", message)[0]

#指定文件夹随机取一个文件，不重复
def getGroupRandomFile(gid : str, dataFlag : str, rootPath : str) -> str:
    global runtime_data
    if runtime_data.get(gid) == None:
            runtime_data[gid] = {}
    if runtime_data.get(gid).get(dataFlag) == None or len(runtime_data.get(gid).get(dataFlag)) == 0:
        fileList = []
        for filePath,dirnames,filenames in os.walk(rootPath):
            for fileName in filenames:
                fileList.append(filePath + "/" + fileName)
        # print(fileList)
        random.shuffle(fileList)
        runtime_data.get(gid)[dataFlag] = fileList
    file = runtime_data.get(gid)[dataFlag].pop()
    return file



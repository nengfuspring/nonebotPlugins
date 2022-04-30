from nonebot import get_driver, on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, MessageEvent, GroupMessageEvent, Message
from nonebot.params import CommandArg
from nonebot.log import logger
from pathlib import Path
import urllib.request
import random
import httpx
import json
import os
import re



__help__plugin_name__ = "daodianle"
__des__ = "网易云评论"
__cmd__ = "到点了"
__short_cmd__ = __cmd__
__example__ = "到点了"
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"

driver = get_driver()
dir_path = Path(__file__).parent
resource_path = dir_path / "resource"
daodian_runtime_data = {}

@driver.on_startup
async def on_botstart():
    global daodian_runtime_data
    try:
        with open(dir_path / "db_record.json", "r", encoding="utf-8") as f:
            daodian_runtime_data = json.load(f)
            f.close()
            if daodian_runtime_data == None:
                daodian_runtime_data = {}
    except:
        daodian_runtime_data = {}

@driver.on_shutdown
async def on_botshutdown():
    dbsave()
    
daodianle = on_command("到点了", priority=5, block=True)
@daodianle.handle()
async def _(event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    gid = str(event.group_id)
    post = getGroupRandomText(gid, "cloud_music")
    imgRoot = getGroupRandomFile(gid, "cloudMusicImg", f"{resource_path}/img/")
    imgPath = f"file:///{imgRoot}"
    try:
        await daodianle.send(MessageSegment.image(imgPath) + MessageSegment.text("\n" + post))
        dbsave()
    except:
        await daodianle.send(MessageSegment.at(event.user_id) + MessageSegment.text("出错了请重试"))



daodianle_add = on_command("添加到点了", priority=3, block=True)
@daodianle_add.handle()
async def add(bot: Bot, event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    global daodian_runtime_data
    gid = str(event.group_id)
    meta = getPicMeta(str(event.message))
    try:
        imgPath = meta[0]
        md5 = str(meta[1]).split(".")[0]
        # img = httpx.get(imgPath)
        saveImgPath = resource_path / "img" / (md5 + ".gif")
        urllib.request.urlretrieve(imgPath, saveImgPath)
        if daodian_runtime_data.get(gid) == None:
            daodian_runtime_data[gid] = {}
        if daodian_runtime_data.get(gid).get("cloudMusicImg") == None:
            temp = getGroupRandomFile(gid, "cloudMusicImg", f"{resource_path}/img/")
        added = False
        if saveImgPath in daodian_runtime_data.get(gid).get("cloudMusicImg"):
            added = True
        if not added:
            daodian_runtime_data.get(gid).get("cloudMusicImg").append(saveImgPath)
        logger.info(f"{__help__plugin_name__}:{str(event.user_id)}:addimg:{md5}")
        dbsave()
        await daodianle_add.send(MessageSegment.text("添加成功~") + MessageSegment.image(imgPath))
    except Exception as e:
        logger.info(f"{__help__plugin_name__}:erro:{str(event.user_id)}:addimg:{md5}:e:{e}")
        await daodianle_add.send(MessageSegment.at(event.user_id) + MessageSegment.text("出错了请重试"))


def dbsave():
    global daodian_runtime_data
    with open(dir_path / "db_record.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(daodian_runtime_data))
        f.close()
    logger.info("daodianle db save succ")


def getPicMeta(message: str):
    return re.findall("url=(.*?)[,|\]]", message)[0], re.findall("file=(.*?)[,|\]]", message)[0]

#json文件随机取一行，不重复
def getGroupRandomText(gid : str, fileName : str) -> str:
    global daodian_runtime_data
    if daodian_runtime_data.get(gid) == None:
            daodian_runtime_data[gid] = {}
    fullName = fileName + ".json"
    if daodian_runtime_data.get(gid).get(fileName) == None or len(daodian_runtime_data.get(gid).get(fileName)) == 0:
        with open(resource_path / fullName, "r", encoding="utf-8") as f:
            cfg = json.load(f).get("post")
        daodian_runtime_data.get(gid)[fileName] = getRandomList(0, len(cfg) - 1)
    index = daodian_runtime_data.get(gid)[fileName].pop()
    post = getIndexText(fullName, index)
    return post

#json文件取指定一行
def getIndexText(fileName : str, index : int) -> list:
    filePath = resource_path / fileName
    with open(filePath, "r", encoding="utf-8") as f:
        cfg = json.load(f).get("post")
    return str(cfg[index])

#生成乱序数列表
def getRandomList(min : int, max : int) -> list:
    list = []
    index = min
    while index <= max:
        list.append(index)
        index += 1
    random.shuffle(list)
    return list

#指定文件夹随机取一个文件，不重复
def getGroupRandomFile(gid : str, dataFlag : str, rootPath : str) -> str:
    global daodian_runtime_data
    if daodian_runtime_data.get(gid) == None:
            daodian_runtime_data[gid] = {}
    if daodian_runtime_data.get(gid).get(dataFlag) == None or len(daodian_runtime_data.get(gid).get(dataFlag)) == 0:
        fileList = []
        for filePath,dirnames,filenames in os.walk(rootPath):
            for fileName in filenames:
                fileList.append(filePath + "/" + fileName)
        # print(fileList)
        random.shuffle(fileList)
        daodian_runtime_data.get(gid)[dataFlag] = fileList
    file = daodian_runtime_data.get(gid)[dataFlag].pop()
    return file
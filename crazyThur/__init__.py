from nonebot import get_driver, on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, MessageEvent, GroupMessageEvent, Message
from nonebot.params import CommandArg
from pathlib import Path
import json
import random


__help__plugin_name__ = "crazyThur"
__des__ = "疯狂星期四文案"
__cmd__ = "疯狂星期四"
__short_cmd__ = __cmd__
__example__ = "疯狂星期四"
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"

driver = get_driver()
dir_path = Path(__file__).parent
resource_path = dir_path / "resource"
crazy_runtime_data = {}

@driver.on_startup
async def on_botstart():
    global crazy_runtime_data
    try:
        with open(dir_path / "db_record.json", "r", encoding="utf-8") as f:
            crazy_runtime_data = json.load(f)
            f.close()
            if crazy_runtime_data == None:
                crazy_runtime_data = {}
    except:
        crazy_runtime_data = {}

@driver.on_shutdown
async def on_botshutdown():
    dbsave()
    
crazy = on_command("疯狂星期四", priority=5, block=True)
@crazy.handle()
async def _(event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    gid = str(event.group_id)
    post = getGroupRandomText(gid, "crazy_thursday")
    await crazy.send(MessageSegment.text(post))
    dbsave()

def dbsave():
    global crazy_runtime_data
    with open(dir_path / "db_record.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(crazy_runtime_data))
        f.close()

#json文件随机取一行，不重复
def getGroupRandomText(gid : str, fileName : str) -> str:
    global crazy_runtime_data
    if crazy_runtime_data.get(gid) == None:
            crazy_runtime_data[gid] = {}
    fullName = fileName + ".json"
    if crazy_runtime_data.get(gid).get(fileName) == None or len(crazy_runtime_data.get(gid).get(fileName)) == 0:
        with open(resource_path / fullName, "r", encoding="utf-8") as f:
            cfg = json.load(f).get("post")
        crazy_runtime_data.get(gid)[fileName] = getRandomList(0, len(cfg) - 1)
    index = crazy_runtime_data.get(gid)[fileName].pop()
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
from nonebot import get_driver, on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, MessageEvent, GroupMessageEvent, Message
from nonebot.params import CommandArg
from pathlib import Path
import re


__help__plugin_name__ = "fakeMsg"
__des__ = "生成假消息"
__cmd__ = "造假@群友1呜呜我不会自己上厕所@群友2笑死"
__short_cmd__ = __cmd__
__example__ = "造假@群友1呜呜我不会自己上厕所@群友2笑死"
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"

driver = get_driver()
dir_path = Path(__file__).parent
resource_path = dir_path / "resource"
runtime_data = {}


fake = on_command("造假", priority=6, block=True)
@fake.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    gid = str(event.group_id)
    if "[CQ:at" in str(event.message):
        member_list = await bot.get_group_member_list(group_id = int(gid))
        post = ""
        try:
            post = fake_msg(str(event.message), member_list)
        except Exception:
            post = "格式不对"
        await bot.send_group_forward_msg(group_id=gid, messages=post)

def fake_msg(text: str, member_list: list) -> list:
    msg = text.replace(" ", "")
    #造假[CQ:at,qq=1052344914]123[CQ:at,qq=1361944419]456
    #['造假', '[CQ:at,qq=279853216]', '1234', '[CQ:face,id=107]', '', '[CQ:at,qq=1361944419]', '222😭']
    parsed = []
    subStr = ""
    for i in range(len(msg)):
        subStr += msg[i]
        if i < len(msg) - 2 and msg[i+1] == "[":
            parsed.append(subStr)
            subStr = ""
        if msg[i] == "]":
            parsed.append(subStr)
            subStr = ""
        if i == len(msg) - 1:
            parsed.append(subStr)
    print(parsed)
    node = list()
    for i in range(len(parsed)):
        if "[CQ:at" in parsed[i] and i < len(parsed) - 1:
            uid = re.findall("\d+", parsed[i])
            content = ""
            for j in range(i+1, len(parsed)):
                if "[CQ:at" not in parsed[j]:
                    content += parsed[j]
                    i += 1
                else:
                    break
            name = uid[0]
            for member in member_list:
                if member["user_id"] == int(uid[0]):
                    name = member["nickname"]
            print(name, content)
            node.append({"type": "node", "data": {"name": name, "uin": uid[0], "content": content}})
    return node
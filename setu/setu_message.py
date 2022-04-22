from json import loads
from pathlib import Path

from anyio import open_file
from nonebot import get_driver
from nonebot.log import logger

from .config import Config

plugin_config = Config.parse_obj(get_driver().config.dict())
if plugin_config.setu_send_custom_message_path:
    MSG_PATH = Path(str(plugin_config.setu_send_custom_message_path)).absolute()
else:
    MSG_PATH = None


async def load_setu_message():
    if MSG_PATH:
        logger.info(f"加载自定义色图消息 路径: {MSG_PATH}")
        async with await open_file(MSG_PATH) as f:  # type: ignore
            f = await f.read()
        return loads(f)
    else:
        return {
            "setu_message_send": [
                
            ],
            "setu_message_cd": [
                "憋冲了！你已经冲不出来了{cd_msg}后可以再次发送哦！",
                "憋住，不准冲！CD:{cd_msg}",
                "你的色图不出来了！还需要{cd_msg}才能出来哦",
                "注意身体，色图看太多对身体不好 (╯‵□′)╯︵┻━┻ 你还需要{cd_msg}才能再次发送哦",
                "憋再冲了！{cd_msg}",
                "呃...好像冲了好多次...感觉不太好呢...{cd_msg}后再冲吧",
                "？？？",
                "你急啥呢？",
                "你这么喜欢色图，{cd_msg}后再给你看哦",
            ],
        }

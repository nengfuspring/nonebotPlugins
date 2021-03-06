from io import BytesIO

from nonebot import get_driver
from nonebot.log import logger
from webdav4.client import Client as dav_client

from .config import Config

plugin_config = Config.parse_obj(get_driver().config.dict())

setu_dav_url = plugin_config.setu_dav_url
setu_dav_username = plugin_config.setu_dav_username
setu_dav_password = plugin_config.setu_dav_password
setu_path = plugin_config.setu_path

logger.info(
    "setu将会保存在 WebDAV 服务器中, URL: {}, UserName: {}, Path: {}".format(
        setu_dav_url, setu_dav_username, setu_path
    )
)


def upload_file(file_obj, pid: str, p: str, r18: bool = False):
    client = dav_client(
        setu_dav_url,  # type: ignore
        auth=(setu_dav_username, setu_dav_password),  # type: ignore
    )
    path = (
        f"{'setu' if not setu_path else setu_path}{'r18' if r18 else '' }/{pid}_{p}.jpg"
    )
    client.upload_fileobj(file_obj, to_path=path, overwrite=True)
    logger.debug(f"WebDAV: {setu_dav_url} 图片已保存{path}")


def convert_file(bytes_file):
    file = BytesIO(bytes_file)
    return file


def save_img(content, pid: str, p: str, r18: bool = False):
    upload_file(convert_file(content), pid, p, r18)

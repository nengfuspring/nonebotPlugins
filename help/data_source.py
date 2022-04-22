import jinja2
from os import getcwd
from typing import List, Optional
from pathlib import Path
from nonebot.log import logger
# from nonebot_plugin_htmlrender import html_to_pic
from .browser import get_new_page, shutdown_browser
# from .date_source import html_to_pic

from .plugin import PluginInfo

dir_path = Path(__file__).parent
template_path = dir_path / "template"
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path), enable_async=True
)


async def get_help_img(event_type: str, plugins: List[PluginInfo]) -> Optional[bytes]:
    try:
        template = env.get_template("help.html")
        content = await template.render_async(type=event_type, plugins=plugins)
        return await html_to_pic(
            content, wait=0, viewport={"width": 100, "height": 100}, template_path=f"file://{str(template_path)}"
        )
    except Exception as e:
        logger.warning(f"Error in get_help_img: {e}")
        return None


async def get_plugin_img(plugin: PluginInfo) -> Optional[bytes]:
    try:
        template = env.get_template("plugin.html")
        content = await template.render_async(plugin=plugin)
        return await html_to_pic(
            content, wait=0, viewport={"width": 500, "height": 100}
        )
    except Exception as e:
        logger.warning(f"Error in get_plugin_img({plugin.name}): {e}")
        return None


async def html_to_pic(
    html: str, wait: int = 0, template_path: str = f"file://{getcwd()}", **kwargs
) -> bytes:
    if "file:" not in template_path:
        raise "template_path 应该为 file:///path/to/template"
    async with get_new_page(**kwargs) as page:
        await page.goto(template_path)
        await page.set_content(html, wait_until="networkidle")
        await page.wait_for_timeout(wait)
        img_raw = await page.screenshot(full_page=True)
        shutdown_browser()
    return img_raw
import traceback
from typing import List, Type
from nonebot import on_command, on_message
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler, T_State
from nonebot.params import CommandArg, State
from dataclasses import dataclass
from typing import List, Tuple, Union
from bs4 import BeautifulSoup
import httpx
import os
import sys
import urllib.request
import httplib2
import math
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    MessageEvent,
    GroupMessageEvent,
)
from nonebot.log import logger

__help__plugin_name__ = "epo"
__des__ = "找谱"
__cmd__ = "简谱/五线谱"
__short_cmd__ = __cmd__
__example__ = " "
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"


project_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".")
# __usage__ = f"{__des__}\n\nUsage:\n{__cmd__}\n\nExamples:\n{__example__}"

epo_main_url = "https://www.everyonepiano.cn"
scoreTypeDic = {"stave":"五线谱","Number":"简谱"}
m = on_command("五线谱", aliases={"简谱"}, block=True, priority=8)
@m.handle()
async def epo(bot: Bot, event: GroupMessageEvent, state: T_State = State()):
    gid = str(event.group_id)
    scoreType = "stave"
    msgStr = str(event.message)
    keykey = msgStr[3:]

    if "简谱" in msgStr:
        keykey = msgStr[2:]
        scoreType = "Number"
    keyWord = urllib.parse.quote(keykey.encode("GBK"))

    musicList = getMusicList(keyWord)
    if len(musicList) == 0:
        await m.send(MessageSegment.text("没找到《" + keykey + "》的谱子"))
    else:
        await m.send(MessageSegment.text("《" + keykey + "》" + scoreTypeDic[scoreType] + " loading..."))
        mostHotId = musicList[0]["id"]
        mostHot = int(musicList[0]["hot"])
        for music in musicList:
            if int(music["hot"]) > mostHot:
                mostHot = int(music["hot"])
                mostHotId = musicList[0]["id"]
        urlList = getImgUrlListById(str(mostHotId), scoreType, True)
        selfInfo = await bot.get_group_member_info(group_id = event.group_id, user_id = event.self_id)
        nickName = selfInfo.get("card", "") or selfInfo.get("nickname", "")
        nodeList = getNodeList(urlList, event.self_id, nickName)
        await bot.send_group_forward_msg(group_id = gid, messages = nodeList)
    

    
    # maxhotid = searchScore(keyWord)
    # if maxhotid == -1:
    #     await m.send(MessageSegment.text("没找到《" + keykey + "》的谱子"))
    # else:
    #     urlList = getImgUrlListById(str(maxhotid), scoreType, False)
    #     selfInfo = await bot.get_group_member_info(group_id = event.group_id, user_id = event.self_id)
    #     nickName = selfInfo.get("card", "") or selfInfo.get("nickname", "")
    #     nodeList = getNodeList(urlList, event.self_id, nickName)
    #     await bot.send_group_forward_msg(group_id = gid, messages = nodeList)

def downloadImg(url: str, fileName: str) -> int:
    urllib.request.urlretrieve(url, fileName)


def searchScore(keyword: str) -> List:
    url = "https://www.everyonepiano.cn/Music-search/?word=" + keyword + "&come=webs"
    response = httpx.get(url)
    soup = BeautifulSoup(response.text)
    MusicIndexBox = soup.find_all(class_='MusicIndexBox')
    maxHot = -1
    maxHotNode = ""
    for boxNode in MusicIndexBox: 
        hot = boxNode.find_all(class_='MIMusicInfo2Num')[0].text
        if int(hot) > maxHot:
            maxHot = int(hot)
            maxHotNode = boxNode
    if maxHot == -1:
        return -1
    epoId = maxHotNode.find_all(class_="MIMusicNO hidden-xs")[0].text
    infoNodes = boxNode.find_all(class_='MITitle')
    for info in infoNodes:
        print(info.text)
    return int(epoId)

#传入epoid返回图片url列表
def getImgUrlListById(epoId: str, scoreType: str, save: bool) -> list:
    urlList = list()
    url: str =  epo_main_url + "/"+ scoreType +"-"+ epoId +"-1-1.html"
    response = httpx.get(url)
    soup = BeautifulSoup(response.text)
    imgUrlAti = soup.find_all(class_='img-responsive DownMusicPNG')[0]
    imgUrl = epo_main_url + imgUrlAti['src']
    urlList.append(imgUrl)
    if save:
        path = project_path + "/resource/epo/"+ epoId
        if not os.path.exists(path):
            os.makedirs(path)
        filePath =  path + "/"+ epoId + "-" + scoreType + "-1.jpg"
        downloadImg(imgUrl, filePath)
    pageCount: int = getPageCount(soup)
    if pageCount > 1:
        for page in range(2, pageCount+1):
            url = epo_main_url + "/" + scoreType + "-" + epoId + "-" + str(page) + "-1.html"
            response = httpx.get(url)
            soup = BeautifulSoup(response.text)
            imgUrlAti = soup.find_all(class_='img-responsive DownMusicPNG')[0]
            imgUrl = epo_main_url + imgUrlAti['src']
            urlList.append(imgUrl)
            if save:
                path = project_path + "/resource/epo/"+ epoId
                if not os.path.exists(path):
                    os.makedirs(path)
                filePath = path + "/"+ epoId + "-" + scoreType + "-" + str(page) +".jpg"
                downloadImg(imgUrl, filePath)
    return urlList


#传入soup返回页数
def getPageCount(soup) -> int:
    h2Div = soup.find_all(class_='EOPStaveH2Div')
    for div in h2Div:
        innerText = div.text
        startIndex: int = innerText.find("共")
        endIndex: int = innerText.find("张")
        if startIndex != -1 and endIndex != -1:
            return int(innerText[startIndex+1 : endIndex])
    return 1


def getNodeList(urlList: list, self_id: int, nickName: str) -> list:
    node = list()
    for url in urlList:
        node.append({"type": "node", "data": {"name": nickName, "uin": self_id, "content": MessageSegment.image(url)}})
    return node


def getMusicList(keyword: str) -> list:
    musicNodeList = list()
    url = epo_main_url + "/Music-search/?word=" + keyword + "&come=webs"
    response = httpx.get(url)
    soup = BeautifulSoup(response.text)
    MusicIndexBox = soup.find_all(class_='MusicIndexBox')
    EOPPageNo = soup.find_all(class_='col-xs-4 col-sm-4 col-md-5 EOPPageNo')[0]
    pageCount = math.ceil(int(EOPPageNo.find_all(class_='EOPRed')[0].text) / 10)
    print(keyword, pageCount, "页")
    if pageCount == 0:
        # with open(project_path + "/resource/notFoundmusichtml"+ keyword +".txt", "w") as f:
        #     f.write(response.text)
        #     f.close()
        return musicNodeList
    for boxNode in MusicIndexBox:
        musicNodeList.append(getMusic(boxNode))
    print("第1页完成")
    #https://www.everyonepiano.cn/Music-search/?come=web&p=2&canshu=cn_edittime&word=%E4%B9%85%E7%9F%B3%E8%AE%A9&author=&jianpu=&paixu=desc&username=
    if pageCount > 10:
        pageCount = 10
    if pageCount > 1:
        for page in range(2, pageCount+1):
            url = epo_main_url + "/Music-search/?word=" + keyword + "&come=webs&p=" + str(page)
            response = httpx.get(url)
            soup = BeautifulSoup(response.text)
            MusicIndexBox = soup.find_all(class_='MusicIndexBox')
            for boxNode in MusicIndexBox:
                musicNodeList.append(getMusic(boxNode))
            print("第", page , "页完成")
    return musicNodeList

def getMusic(boxNode):
    hot = boxNode.find_all(class_='MIMusicInfo2Num')[0].text
    epoId = boxNode.find_all(class_="MIMusicNO hidden-xs")[0].text
    # return Music(id = epoId, hot = hot)
    return {"hot": hot, "id": epoId}

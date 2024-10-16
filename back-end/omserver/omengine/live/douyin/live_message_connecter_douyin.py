import os
from sre_parse import TYPE_FLAGS

from dotenv import load_dotenv

# from ..live_message import LiveMessage, put_message

import json
import logging

logger = logging.getLogger(__name__)

load_dotenv()

# import dybullet
# class DouyinConnecter():
#     _room_id : str
#     _bullet: any
#     _danmu_list: any
#     def __init__(self) -> None:
#         dybullet.init()  # 初始化dybullet
#         super().__init__()
#     async def loadLiveConfig(self) -> str:
#         self._room_id = '123456'  # 直播间ID
#         self._bullet = dybullet.Bullet(self._room_id)
#     async def startLive(self) -> str:
#         self._bullet.start()  # 开始监听弹幕
#         self._danmu_list = self._bullet.get_bullet()  # 获取弹幕列表
#         # 输出弹幕列表
#         print(self._danmu_list)
#     async def stopLive(self):
#         self._bullet.stop()  # 停止监听弹幕

 
# from mitmproxy import ctx
#
# class DanmuCapture:
#     def __init__(self):
#         self.danmu_list = []
 
#     def response(self, flow):
#         # 判断请求是否是抖音直播弹幕请求
#         if "douyin.com/live/bullet/liveshow" in flow.request.url:
#             # 解析响应数据
#             response_data = json.loads(flow.response.text)
#             # 获取弹幕列表
#             danmu_list = response_data['data']['comments']
#             for danmu in danmu_list:
#                 self.danmu_list.append(danmu['comment'])
 
#     def done(self):
#         # 输出弹幕列表
#         print(self.danmu_list)
 
# addons = [
#     DanmuCapture()
# ]

def main():
    pass

class DouyinLiveClient():
    room_id: str
    uid: int = 0
    cookie_str: str

    def __init__(self) -> None:
        logger.debug("====================== init DouyinLiveClient ====================== ")
        self.room_id = os.environ['ROOM_ID_BILI']
        uid = os.environ['ROOM_UID_BILI']
        if uid:
            self.uid = int(uid)
        self.cookie_str = os.environ['ROOM_COOKIE_BILI']
        logger.debug(f"=> room_id:{ self.room_id}")
        logger.debug(f"=> uid:{self.uid}")
        logger.debug(f"=> cookie_str:{self.cookie_str}")
        logger.info("=> Init DouyinLiveClient Success")

    async def start(self):
        
        pass

    async def stop(self):
        self.client.join()
        self.client.stop_and_close()
        logger.info("=> Stop DouyinLiveClient Success")


class DouyinHandler():

    room_id: str

    def __init__(self, room_id: str) -> None:
        super().__init__()
        self.room_id = room_id
    # async def _on_danmaku(self, client: DouyinLiveClient, message: DanmakuMessage):
    #     put_message(LiveMessage(
    #         type="danmaku", user_name=message.uname, content=message.msg, emote="neutral", action=""))

    # async def _on_interact_word(self, client: DouyinLiveClient, message: InteractWordMessage):
    #     """
    #     用户进入直播间，用户关注直播间
    #     """
    #     message_str = f'{message.uname}进入了直播间，欢迎欢迎'
    #     put_message(LiveMessage(
    #         type="danmaku", user_name=message.uname, content=message_str, emote="happy", action="fbx/standing_greeting.fbx"))

# enable_bili_live = False

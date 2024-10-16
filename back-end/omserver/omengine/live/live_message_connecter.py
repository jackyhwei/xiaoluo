from abc import ABC, abstractmethod
import asyncio
import logging
import os
import threading
from .bilibili.live_message_connecter_bili import BiliLiveClient
from .douyin.live_message_connecter_douyin import DouyinLiveClient
from .live_message import send_message

# 创建一个线程安全的队列
# insight_message_queue = queue.SimpleQueue()
logger = logging.getLogger(__name__)

class LiveConnecterTask():
    @staticmethod
    def start():
        # 创建后台线程
        background_thread = threading.Thread(target=send_message)
        background_thread.daemon = True
        
        # 启动后台线程
        background_thread.start()
        logger.info("=> Start InsightMessageQueryJobTask Success")


class BaseLiveConnecter(ABC):
    @abstractmethod
    async def loadLiveConfig(self) -> str:
        pass

    @abstractmethod
    async def startLive(self) -> str:
        pass

    @abstractmethod
    async def stopLive(self):
        pass


# 定义策略类实现
class LiveConnecter_Bili(BaseLiveConnecter):
    liveClient_bili: BiliLiveClient
    def __init__(self) -> None:
        super().__init__()
        self.liveClient_bili = BiliLiveClient()

    async def loadLiveConfig(self) -> str:
        pass

    async def startLive(self) -> str:
        pass

    async def stopLive(self):
        pass

class LiveConnecter_Douyin(BaseLiveConnecter):
    liveClient_bili: DouyinLiveClient
    def __init__(self) -> None:
        super().__init__()
        self.liveClient_bili = BiliLiveClient()

    async def loadLiveConfig(self) -> str:
        pass

    async def startLive(self) -> str:
        pass

    async def stopLive(self):
        pass


class LiveDriver:
    def __init__(self):
        self.chat_stream_lock = threading.Lock()

    async def loadLiveConfig(self, type: str) -> str:
        strategy = self.get_strategy(type)
        return strategy.loadLiveConfig()

    async def startLive(self, type: str) -> str:
        strategy = self.get_strategy(type)
        return strategy.startLive()

    async def stopLive(self, type: str):
        strategy = self.get_strategy(type)
        return strategy.stopLive()

    def get_strategy(self, type: str) -> BaseLiveConnecter:
        if type == "bilibili":
            return LiveConnecter_Bili()
        elif type == "douyin":
            return LiveConnecter_Douyin()
        else:
            # raise ValueError("Unknown type")
            print("!!!!!!!!!!!!!!!!!!Unknown live connecter type, default as bilibili. !!!!!!!!!!!!!")
            return LiveConnecter_Bili()


def live_connecter_main():
#     global enable_bili_live
#    if enable_bili_live == True:
    enable_bili_live = os.environ['live_connecter_enabled']

    if True == enable_bili_live:
        background_thread = threading.Thread(target=start_live_client)
        # 将后台线程设置为守护线程，以便在主线程结束时自动退出
        background_thread.daemon = True
        # 启动后台线程
        background_thread.start()
        enable_bili_live = True
        logger.info("=> Start LiveClient Success")

def start_live_client():
    client = BiliLiveClient()
    asyncio.run(client.start())


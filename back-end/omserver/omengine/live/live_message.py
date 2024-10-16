from abc import ABC, abstractmethod
import asyncio
import logging
import os
import queue
import threading
import traceback
from ..utils.chat_message_utils import format_user_chat_text
from ...mainservice import singleton_main_service
from ...mainservice.output import realtime_message_queue

# 创建一个线程安全的队列
live_message_queue = queue.SimpleQueue()
logger = logging.getLogger(__name__)

class LiveMessage():

    type: str
    user_name: str
    content: str
    emote: str
    action: str
    expand: str

    def __init__(self, type: str, user_name: str, content: str, emote: str, action: str = None, expand: str = None) -> None:
        self.type = type
        self.user_name = user_name
        self.content = content
        self.emote = emote
        self.action = action
        self.expand = expand

    def to_dict(self):
        return {
            "type": self.type,
            "user_name": self.user_name,
            "content": self.content,
            "emote": self.emote,
            "action": self.action,
            "expand": self.expand
        }


def put_message(message: LiveMessage):
    global live_message_queue
    live_message_queue.put(message)


def send_message():
    while True:
        try:
            message = live_message_queue.get()
            if (message != None and message != ''):
                if (message.type == "danmaku"):
                    content = format_user_chat_text(text=message.content)
                    realtime_message_queue.put_message(realtime_message_queue.RealtimeMessage(
                        type=message.type,
                        user_name=message.user_name,
                        content=content,
                        emote=message.emote,
                        action=message.action
                    ))
                    singleton_process_core.chat(
                        your_name=message.user_name, query=message.content)
        except Exception as e:
            traceback.print_exc()


import logging
from omserver.mainservice.messages.chat_live_message import ChatLiveMessage, put_message

logger = logging.getLogger(__name__)

class Notifier_WebClient():

    @staticmethod
    def notify(title: str, content: str, target_user: str, **kwargs) -> str:
        put_message(ChatLiveMessage(type="user", user_name="sys", query=title, role_name="agent", content=content, emote="neutral"))
    
import logging
from omserver.mainservice.output.realtime_message_queue import RealtimeMessage, put_message

logger = logging.getLogger(__name__)

class Notifier_WebClient():

    @staticmethod
    def notify(title: str, content: str, target_user: str, **kwargs) -> str:
        put_message(RealtimeMessage(type="user", user_name="sys", query=title, role_name="agent", content=content, emote="neutral"))
    
import logging

logger = logging.getLogger(__name__)

class Notifier_Wechat():

    @staticmethod
    def notify(title: str, content: str, target_user: str, **kwargs) -> str:
        logger.error(f"wechat notification to be implemented")
    
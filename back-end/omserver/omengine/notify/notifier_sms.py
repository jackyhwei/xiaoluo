import logging

logger = logging.getLogger(__name__)

class Notifier_Sms():

    @staticmethod
    def notify(title: str, content: str, target_user: str, **kwargs) -> str:
        logger.error(f"sms notification to be implemented")
 
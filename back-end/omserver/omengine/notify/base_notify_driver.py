from abc import ABC, abstractmethod

from .notifier_email import Notifier_Email
from .notifier_sms import Notifier_Sms
from .notifier_wechat import Notifier_Wechat
from .notifier_alarmclock import Notifier_AlarmClock
from .notifier_webclient import Notifier_WebClient

class BaseNotifyDriver(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def notify(self, title: str, content: str, target_user: str, **kwargs) -> str:
        pass

class EmailNofityDriver(BaseNotifyDriver):
    def __init__(self) -> None:
        pass

    def notify(self, title: str, content: str, target_user: str, **kwargs) -> str:
        Notifier_Email.notify(title=title, content=content, target_user=target_user)

class WechatNotifyDriver(BaseNotifyDriver):
    def __init__(self) -> None:
        pass
    def notify(self, title: str, content: str, target_user: str, **kwargs) -> str:
        Notifier_Wechat.notify(title=title, content=content, target_user=target_user)

class SmsNotifyDriver(BaseNotifyDriver):
    def __init__(self) -> None:
        pass
    def notify(self, title: str, content: str, target_user: str, **kwargs) -> str:
        Notifier_Sms.notify(title=title, content=content, target_user=target_user)

class AlarmClockNotifyDriver(BaseNotifyDriver):
    '''
    XXX 不知道未来会不会真的会出AI手机，把LLM安装到手机上？
        不然的话，omserver不应该安装到手机上，也不可能有闹钟提醒的模式
    '''
    def __init__(self) -> None:
        pass
    def notify(self, title: str, content: str, target_user: str, **kwargs) -> str:
        Notifier_AlarmClock.notify(title=title, content=content, target_user=target_user)

class WebClientNotifyDriver(BaseNotifyDriver):
    def __init__(self) -> None:
        pass
    def notify(self, title: str, content: str, target_user: str, **kwargs) -> str:
        Notifier_WebClient.notify(title=title, content=content, target_user=target_user)

class NotifyDriver:
    def Notify(self, title: str, content: str, target_user:str, type: str, **kwargs) -> str:
        # print("11111111111")
        notifier = self.get_strategy(type=type)
        # print("22222222222")
        result = notifier.notify(title=title, content=content, target_user=target_user, kwargs=kwargs)
        # print("33333333333")
        return result;

    '''Notify驱动类'''
    def get_strategy(self, type: str) -> BaseNotifyDriver:
        if type == "email":
            return EmailNofityDriver()
        elif type == "wechat":
            return WechatNotifyDriver()
        elif type == "sms":
            return SmsNotifyDriver()
        elif type == "alarmclock":
            return AlarmClockNotifyDriver()
        elif type == "webclient":
            return WebClientNotifyDriver()
        else:
            raise ValueError(f"Unknown type:{type}")

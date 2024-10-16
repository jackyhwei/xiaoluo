import logging
from abc import ABC, abstractmethod

from .google.translator_google import Translator_Google
from .huoshan.translator_huoshan import Translator_HuoShan
from .youdao.translator_youdao import Translator_Youdao

logger = logging.getLogger(__name__)

class BaseTranslator(ABC):
    '''翻译抽象类'''

    @abstractmethod
    def translate(self, text: str, target_language: str) -> str:
        '''翻译抽象接口'''
        pass

class TranslationHuoshan(BaseTranslator):
    def translate(self, text: str, target_language: str) -> str:
        '''火山翻译'''
        pass

class TranslationGoogle(BaseTranslator):
    def translate(self, text: str, target_language: str) -> str:
        '''Google翻译'''
        pass

class TranslationYoudao(BaseTranslator):
    def translate(self, text: str, target_language: str) -> str:
        '''有道翻译'''
        pass


class TranslationDriver(ABC):

    def translate(self, type: str, text: str, target_language: str, **kwargs) -> str:
        translate = self.loadDriver(type)
        result = translate.translate(text=text, target_language=target_language, kwargs=kwargs)
        logger.info(f"Translation # type:{type} text:{text} => result: {result} #")
        return result

    def loadDriver(self, type: str) -> BaseTranslator:
        if type == "Youdao":
            return TranslationYoudao()
        elif type == "Huoshan":
            return TranslationHuoshan()
        elif type == "Google":
            return TranslationGoogle()
        else:
            raise ValueError("Unknown type")

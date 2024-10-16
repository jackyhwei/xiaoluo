from abc import ABC, abstractmethod
import logging
from .tts_edge import TTS_Edge, TTS_edge_voices
from .tts_bert_vits2 import TTS_BertVits2
from .tts_omserver import TTS_OMServer

logger = logging.getLogger(__name__)

class BaseTTS(ABC):

    '''合成语音统一抽象类'''

    @abstractmethod
    def synthesis(self, text: str, voice_id: str, **kwargs) -> str:
        '''合成语音'''
        pass

    @abstractmethod
    def get_voices(self) -> list[dict[str, str]]:
        '''获取声音列表'''
        pass


class TTSEdge(BaseTTS):

    '''Edge 微软语音合成类'''

    def synthesis(self, text: str, voice_id: str, **kwargs) -> str:
        print("1a")
        return TTS_Edge.create_audio(text=text, voiceId=voice_id)

    def get_voices(self) -> list[dict[str, str]]:
        return TTS_edge_voices


class TTSBertVITS2(BaseTTS):
    '''Bert-VITS2 语音合成类'''
    def synthesis(self, text: str, voice_id: str, **kwargs) -> str:
        noise = kwargs.get("noise", "0.5")
        noisew = kwargs.get("noisew", "0.9")
        sdp_ratio = kwargs.get("sdp_ratio", "0.2")
        return TTS_BertVits2.synthesis(text=text, speaker=voice_id, noise=noise, noisew=noisew, sdp_ratio=sdp_ratio)

    def get_voices(self) -> list[dict[str, str]]:
        return TTS_BertVits2.get_voices()

class TTSOMServer(BaseTTS):
    def synthesis(self, text: str, voice_id: str, **kwargs) -> str:
        noise = kwargs.get("noise", "0.5")
        noisew = kwargs.get("noisew", "0.9")
        sdp_ratio = kwargs.get("sdp_ratio", "0.2")
        return TTS_OMServer.synthesis(text=text, speaker=voice_id, noise=noise, noisew=noisew, sdp_ratio=sdp_ratio)

    def get_voices(self) -> list[dict[str, str]]:
        return TTS_OMServer.get_voices()

class TTSDriver:

    '''TTS驱动类'''

    def synthesis(self, type: str, text: str, voice_id: str, **kwargs) -> str:
        # print("11111111111")
        tts = self.get_strategy(type)
        # print("22222222222")
        file_name = tts.synthesis(text=text, voice_id=voice_id, kwargs=kwargs)
        # print("33333333333")
        # logger.info(f"TTS synthesis # type:{type} text:{text} => file_name: {file_name} #")
        return file_name;

    def get_voices(self, type: str) -> list[dict[str, str]]:
        tts = self.get_strategy(type)
        return tts.get_voices()

    def get_strategy(self, type: str) -> BaseTTS:
        if type == "Edge":
            return TTSEdge()
        elif type == "Bert-VITS2":
            return TTSBertVITS2()
        elif type == "omtts":
            return TTSOMServer()
        else:
            raise ValueError("Unknown type")

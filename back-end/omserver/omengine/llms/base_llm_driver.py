from __future__ import annotations
from abc import ABC, abstractmethod
import threading
import asyncio
import os
import logging

from .openai.openai_chat_robot import OpenAIGeneration
from .text_generation.text_generation_chat_robot import TextGeneration
from .baidu.ernie_sdk import ErnieGeneration

from omserver.omengine.llms.langchain.langchain_chat_robot import LangchainGeneration

logger = logging.getLogger(__name__)

class BaseLLM(ABC):
    
    @abstractmethod
    def chat(self, prompt: str, role_name: str, your_name: str, query: str, kb_id: str, short_history: list[dict[str, str]], long_history: str) -> str:
        pass

    @abstractmethod
    async def chatStream(self,
                         prompt: str,
                         role_name: str,
                         your_name: str,
                         query: str,
                         kb_id: str,
                         history: list[dict[str, str]],
                         realtime_callback=None,
                         conversation_end_callback=None,
                         chat_id: str=None,
                         role_id: int=None,
                         user_id: int=None,
                         emotion: str=None,
                         llm_type: str=None,
                         user_ip:str=None
                         ):
        pass


# 定义策略类实现
class LLM_OpenAI(BaseLLM):

    openai_generation: OpenAIGeneration

    def __init__(self) -> None:
        super().__init__()
        self.openai_generation = OpenAIGeneration()

    def chat(self, prompt: str, role_name: str, your_name: str, query: str, kb_id:str, short_history: list[dict[str, str]], long_history: str) -> str:
        return self.openai_generation.chat(prompt=prompt, role_name=role_name, your_name=your_name, query=query, kb_id=kb_id, short_history=short_history, long_history=long_history)

    async def chatStream(self,
                         prompt: str,
                         role_name: str,
                         your_name: str,
                         query: str,
                         kb_id: str,
                         history: list[dict[str, str]],
                         realtime_callback=None,
                         conversation_end_callback=None,
                         chat_id: str=None,
                         role_id: int=0,
                         user_id: int=0,
                         emotion: str=None,
                         llm_type: str=None,
                         user_ip:str=None
                         ):
        return await self.openai_generation.chatStream(prompt=prompt,
                                                       role_name=role_name,
                                                       your_name=your_name,
                                                       query=query,
                                                       kb_id=kb_id,
                                                       history=history,
                                                       realtime_callback=realtime_callback,
                                                       conversation_end_callback=conversation_end_callback,
                                                       chat_id=chat_id,
                                                       role_id=role_id,
                                                       user_id=user_id,
                                                       emotion=emotion,
                                                       llm_type=llm_type,
                                                       user_ip=user_ip
                                                       )

class LLM_Langchain(BaseLLM):
    generation: LangchainGeneration

    def __init__(self, query: str, user_id: int) -> None:
        super().__init__()
        self.generation = LangchainGeneration(user_id=user_id, query=query)
    
    def chat(self, prompt: str, role_name: str, your_name: str, query: str, kb_id: str, short_history: list[dict[str, str]], long_history: str) -> str:
        return self.generation.chat(prompt=prompt, role_name=role_name, your_name=your_name, query=query, kb_id=kb_id, short_history=short_history, long_history=long_history)

    async def chatStream(self, prompt: str, role_name: str, your_name: str, query: str, kb_id: str, 
                         history: list[dict[str, str]],
                         realtime_callback=None, conversation_end_callback=None, 
                         chat_id: str=None, role_id: int=0, user_id: int=0, emotion: str=None, llm_type: str=None, user_ip:str=None
                         ):
        return await self.generation.chatStream(prompt=prompt, role_name=role_name, your_name=your_name, query=query,
                                                kb_id=kb_id, history=history,
                                                realtime_callback=realtime_callback, conversation_end_callback=conversation_end_callback,
                                                chat_id=chat_id, role_id=role_id, user_id=user_id, emotion=emotion, llm_type=llm_type, user_ip=user_ip
                                                )

class LLM_TextGen(BaseLLM):

    generation: TextGeneration

    def __init__(self) -> None:
        super().__init__()
        self.generation = TextGeneration()

    def chat(self, prompt: str, role_name: str, your_name: str, query: str, kb_id: str, short_history: list[dict[str, str]], long_history: str) -> str:
        return self.generation.chat(prompt=prompt, role_name=role_name, your_name=your_name, query=query, kb_id=kb_id, short_history=short_history, long_history=long_history)

    async def chatStream(self,
                         prompt: str,
                         role_name: str,
                         your_name: str,
                         query: str,
                         kb_id: str,
                         history: list[dict[str, str]],
                         realtime_callback=None,
                         conversation_end_callback=None,
                         chat_id: str=None,
                         role_id: int=0,
                         user_id: int=0,
                         emotion: str=None,
                         llm_type: str=None,
                         user_ip:str=None
                         ):
        return await self.generation.chatStream(prompt=prompt,
                                                role_name=role_name,
                                                your_name=your_name,
                                                query=query,
                                                kb_id=kb_id,
                                                history=history,
                                                realtime_callback=realtime_callback,
                                                conversation_end_callback=conversation_end_callback,
                                                chat_id=chat_id,
                                                role_id=role_id,
                                                user_id=user_id,
                                                emotion=emotion,
                                                llm_type=llm_type,
                                                user_ip=user_ip)


class LLM_ERNIE(BaseLLM):

    generation: ErnieGeneration

    def __init__(self) -> None:
        super().__init__()
        self.generation = ErnieGeneration()

    def chat(self, prompt: str, role_name: str, your_name: str, query: str, kb_id: str, short_history: list[dict[str, str]], long_history: str) -> str:
        return self.generation.chat(prompt=prompt, role_name=role_name, your_name=your_name, query=query, kb_id=kb_id, short_history=short_history, long_history=long_history)

    async def chatStream(self, prompt: str, role_name: str, your_name: str, query: str, kb_id: str, history: list[dict[str, str]],
                         realtime_callback=None, conversation_end_callback=None,
                         chat_id: str=None, role_id: int=0, user_id: int=0, emotion: str=None, llm_type: str=None, user_ip:str=None
                         ):
        return await self.generation.chatStream(prompt=prompt, role_name=role_name, your_name=your_name, query=query, kb_id=kb_id,
                                                history=history,
                                                realtime_callback=realtime_callback, conversation_end_callback=conversation_end_callback,
                                                chat_id=chat_id, role_id=role_id, user_id=user_id,
                                                emotion=emotion, llm_type=llm_type, user_ip=user_ip)


class LLMDriver:

    def __init__(self):
        self.chat_stream_lock = threading.Lock()

    def chat(self, prompt: str, type: str, role_name: str, your_name: str, query: str, kb_id: str, short_history: list[dict[str, str]], long_history: str) -> str:
        strategy = self.get_strategy(type)
        result = strategy.chat(prompt=prompt, role_name=role_name,
                               your_name=your_name, query=query, kb_id=kb_id, short_history=short_history, long_history=long_history)
        return result

    def chatStream(self,
                prompt: str,
                type: str,
                role_name: str,
                your_name: str,
                query: str,
                kb_id: str, 
                history: list[dict[str, str]],
                realtime_callback=None,
                conversation_end_callback=None,
                chat_id: str=None,
                role_id: int=0,
                user_id: int=0,
                emotion: str=None,
                llm_type: str=None,
                user_ip:str=None
                ):
        strategy = self.get_strategy(type, query, user_id)
        asyncio.run(strategy.chatStream(prompt=prompt,
                                        role_name=role_name,
                                        your_name=your_name,
                                        query=query,
                                        kb_id=kb_id,
                                        history=history,
                                        realtime_callback=realtime_callback,
                                        conversation_end_callback=conversation_end_callback,
                                        chat_id=chat_id,
                                        role_id=role_id,
                                        user_id=user_id,
                                        emotion=emotion,
                                        llm_type=llm_type,
                                        user_ip=user_ip))

    def get_strategy(self, type: str, query: str =None, user_id: int=None) -> BaseLLM:

        # type = "openai"
        # type = "langchain"
        if type == "":
            logger.warn(f"get_strategy: type is not specified, try retrieve from environ")
            type = os.environ.get("LLM_TYPE", "ernie")
            logger.warn(f"get_strategy: type retrieved from environ={type}")

        if type == "openai":
            return LLM_OpenAI()
        elif type == "text_generation":
            return LLM_TextGen()
        elif type == "langchain":
            return LLM_Langchain(query, user_id)
        elif type == "ernie":
            return LLM_ERNIE()
        else:
            # raise ValueError("Unknown type")
            print("!!!!!!!!!!!!!!!!!!Unknown llm model type, default as chatgpt. !!!!!!!!!!!!!")
            return LLM_OpenAI()
            

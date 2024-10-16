import logging
import os
from typing import List

from openai import OpenAI

from ...utils.str_utils import filter_spaces_and_tabs, filter_tabs, filter_html_tags
from ...utils.chat_message_utils import format_chat_text

logger = logging.getLogger(__name__)


class OpenAIGeneration():

    llm: OpenAI
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    llm_api_key: str
    llm_base_url: str
    max_tokens: int = 50

    def __init__(self) -> None:
        from dotenv import load_dotenv
        load_dotenv()
        self.llm_api_key = os.environ.get('LLM_API_KEY', "sk-cCwAxfqbrU2DlKVIA6B36b75B4924eE09e9eCbD378B7B3Be")
        self.llm_base_url = os.environ.get('LLM_BASE_URL', "https://rg4.net/v1")
        self.model_name = os.environ.get('LLM_MODEL', "gpt-3.5-turbo")
        self.max_tokens = os.environ.get('LLM_MAX_TOKENS', 50)

        # self.llm_api_key = "sk-cCwAxfqbrU2DlKVIA6B36b75B4924eE09e9eCbD378B7B3Be"
        # self.llm_base_url = "https://rg4.net/v1"
        # self.model_name = "Qwen-7B-Chat"
        print("=================================================")
        print("=================================================")
        print(f"OpenAIGeneration, model={self.model_name}, URL={self.llm_base_url}, LLM_API_KEY={self.llm_api_key}")
        print("=================================================")
        print("=================================================")

        if self.llm_base_url != None and self.llm_base_url != "":
            self.llm = OpenAI(api_key=self.llm_api_key, base_url=self.llm_base_url)
        else:
            self.llm = OpenAI(api_key=self.llm_api_key)

    def chat(self, prompt: str, role_name: str, your_name: str, query: str, kb_id: str, short_history: list[dict[str, str]], long_history: str) -> str:
        # FIXME jacky, we shouldn't add prompt to query in agent mode, disable it temparary
        messages = []
        # prompt
        messages.append({'role': 'system', 'content': prompt})
        # # 知识库
        # messages.append({"role": "system", "content": oddmeta_server_kb})
        # history
        for item in short_history:
            message = {"role": "user", "content": item["human"]}
            messages.append(message)
            message = {"role": "assistant", "content": item["ai"]}
            messages.append(message)

        # user message
        # FIXME if this is used to generate emotion for a specified sentence of AI, the "role" should be assistant, and "your_name" should be a role_name
        # messages.append({'role': 'user', 'content': your_name + "说：" + query})
        messages.append({'role': 'assistant', 'content': query})

        response = self.llm.chat.completions.create(
            model=self.model_name, 
            messages=messages, 
            max_tokens=self.max_tokens) 

        llm_result_text = response.choices[0].message.content
        print(f"response={llm_result_text}")

        return llm_result_text

    async def chatStream(self,
                         prompt: str,
                         role_name: str,
                         your_name: str,
                         query: str,
                         kb_id: str,
                         history: list[dict[str, str]],
                         realtime_callback=None,
                         conversation_end_callback=None,
                         chat_id:str=None,
                         role_id:int=0,
                         user_id:int=0,
                         emotion:str=None,
                         llm_type:str=None,
                         user_ip:str=None
                         ):
        # logger.debug(f"prompt:{prompt}")
        messages = []
        # prompt
        messages.append({'role': 'system', 'content': prompt})
        # # TODO Knowledge Base(知识库) mode to be implemented
        # messages.append({"role": "system", "content": oddmeta_server_kb})
        # history
        for item in history:
            message = {"role": "user", "content": item["human"]}
            messages.append(message)
            message = {"role": "assistant", "content": item["ai"]}
            messages.append(message)
        # user message
        messages.append({'role': 'user', 'content': your_name + "说：" + query})

        logger.debug(f"final question: kb_id={kb_id}, your_name={your_name}, role_name={role_name}, message={messages}")

        response = self.llm.chat.completions.create(
            model=self.model_name, 
            messages=messages, 
            stream=True, 
            max_tokens=self.max_tokens) 

        # create variables to collect the stream of chunks
        answer = ""

        for chunk in response:
            content = ""
            end_bool = False
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                if content == " " or content == "\\r\\n" or content == "\\n" or content == "" or chunk.choices[0].finish_reason:
                    end_bool = True

                # FIXME jacky：中文的时候需要过滤空格和制表符，但是英文又不能过滤空格，怎么办？
                # content = filter_spaces_and_tabs(content)
                content = filter_html_tags(content)
                content = filter_tabs(content)
                answer += content

                # logger.debug(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^chatStream:realtime_callback, answer={answer}")
                if realtime_callback:
                    realtime_callback(role_name, your_name, query, content, kb_id, end_bool, chat_id, role_id, user_id, emotion, llm_type, user_ip)  # 调用实时消息推送的回调函数

            if chunk.choices[0].finish_reason:
                # logger.debug(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^chatStream:conversation_end_callback, answer={answer}")
                if conversation_end_callback:
                    conversation_end_callback(role_name, answer, your_name, query, kb_id, chat_id, role_id, user_id, emotion, llm_type, user_ip)  # 调用对话结束消息的回调函数
                break

        print(f"final answer: {answer}")

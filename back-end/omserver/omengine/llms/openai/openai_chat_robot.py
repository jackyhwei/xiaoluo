import logging
import os

# from langchain.chat_models import ChatOpenAI
#from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
# from openai import OpenAI

from langchain.schema import (
    HumanMessage,
)

from ...utils.str_utils import remove_spaces_and_tabs, remove_tabs

logger = logging.getLogger(__name__)


class OpenAIGeneration():

    # llm: OpenAI
    llm: ChatOpenAI

    def __init__(self) -> None:
        from dotenv import load_dotenv
        load_dotenv()
        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
        OPENAI_BASE_URL = os.environ['OPENAI_BASE_URL']
        OPENAI_MODEL = os.environ['OPENAI_MODEL']

        if OPENAI_MODEL == None or OPENAI_MODEL == "":
            OPENAI_MODEL = "gpt-3.5-turbo"

        # OPENAI_API_KEY = "sk-cCwAxfqbrU2DlKVIA6B36b75B4924eE09e9eCbD378B7B3Be"
        # OPENAI_BASE_URL = "https://rg4.net/v1"
        # OPENAI_MODEL = "Qwen-7B-Chat"
        print("=================================================")
        print("=================================================")
        print(f"OpenAIGeneration, model={OPENAI_MODEL}, URL={OPENAI_BASE_URL}, OPENAI_API_KEY={OPENAI_API_KEY}")
        print("=================================================")
        print("=================================================")

        if OPENAI_BASE_URL != None and OPENAI_BASE_URL != "":
            # self.llm = OpenAI(model=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, openai_api_base=OPENAI_BASE_URL)
            self.llm = ChatOpenAI(streaming=True, model_name=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, openai_api_base=OPENAI_BASE_URL, temperature=0.7, verbose=True)
        else:
            # self.llm = OpenAI(model=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY)
            self.llm = ChatOpenAI(streaming=True, model_name=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, temperature=0.7, verbose=True)

    def chat(self, prompt: str, role_name: str, your_name: str, query: str, kb_id: str, short_history: list[dict[str, str]], long_history: str) -> str:
        # FIXME jacky, maybe we shouldn't add query to prompt, disable it temparary
        # prompt = prompt + query
        # logger.debug(f"prompt:{prompt}")
        llm_result = self.llm.generate(messages=[[HumanMessage(content=prompt)]])
        llm_result_text = llm_result.generations[0][0].text
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
        for item in history:
            message = {"role": "user", "content": item["human"]}
            messages.append(message)
            message = {"role": "assistant", "content": item["ai"]}
            messages.append(message)
        messages.append({'role': 'system', 'content': prompt})
        messages.append({'role': 'user', 'content': your_name + "说：" + query})
        # messages.append({'role': 'user', 'content': query})

        OPENAI_MODEL = os.environ['OPENAI_MODEL']
        # print("------------------------------model=", OPENAI_MODEL)
        if OPENAI_MODEL == None or OPENAI_MODEL == "":
            OPENAI_MODEL = "gpt-3.5-turbo"

        logger.debug(f"------------------------------kb_id={kb_id}, your_name={your_name}, role_name={role_name}, message={messages}")

        # TODO Knowledge Base mode to be implemented

        response = self.llm.generate(
            messages=messages,
        )
        # response = self.llm.chat.completions.create(
        #     model=OPENAI_MODEL,
        #     messages=messages,
        #     temperature=0,
        #     stream=True  # again, we set stream=True
        # )

        logger.debug(f"\n\n\nLLM response={response}\n\n\n")

        # create variables to collect the stream of chunks
        answer = ''
        for part in response:
            # print(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^response part={part}")
            finish_reason = part["choices"][0]["finish_reason"]

            if finish_reason:
                '''回答结束
                '''
                logger.debug(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^chatStream:conversation_end_callback, answer={answer}")
                if conversation_end_callback:
                    # def my_conversation_end_callback(role_name: str,  role_message: str, your_name: str, your_message: str, kb_id: str,
                    #              chat_id: str,
                    #              role_id: str,
                    #              user_id: str,
                    #              emotion: str,
                    #              llm_type: str,
                    #              user_ip: str
                    #              ):
                    conversation_end_callback(role_name, answer, your_name, query, kb_id, chat_id, role_id, user_id, emotion, llm_type, user_ip)  # 调用对话结束消息的回调函数
                break  # 停止循环，对话已经结束
            elif "content" in part["choices"][0]["delta"]:
                content = part["choices"][0]["delta"]["content"]
                # FIXME jacky：中文的时候需要过滤空格和制表符，但是英文又不能过滤空格，怎么办？
                # content = remove_spaces_and_tabs(content)
                content = remove_tabs(content)

                if content == "":
                    continue
                answer += content
                # logger.debug(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^chatStream:realtime_callback, answer={answer}")
                if realtime_callback:
                    realtime_callback(role_name, your_name, query, content, kb_id, False, chat_id, role_id, user_id, emotion, llm_type, user_ip)  # 调用实时消息推送的回调函数

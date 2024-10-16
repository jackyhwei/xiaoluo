import abc
import math
import logging
from typing import Any
from datetime import datetime
from langchain.tools import BaseTool
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseOutputParser

from .OddMetaTools import OddMetaToolsBase
import ast
import json

from omserver.omengine.utils.datatime_utils import get_current_time

logger = logging.getLogger(__name__)
    
class CommaSeparatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""

    def parse(self, text: str):
        """Parse the output of an LLM call."""

        print("================================")
        print(f"CommaSeparatedListOutputParser:{text}")
        print("================================")

        return text.strip()

class QueryRecurring(BaseTool, OddMetaToolsBase):
    name = "QueryLoopType"
    description = "用于查询指定任务是否有循环.\
请选择以下几种输出格式进行输出：0是单次任务不循环,1是每天循环、2是每周循环、3是每月循环、4是每年循环."

    def __init__(self, user_id: int=0, original_input: str=None):
        super().__init__()
        OddMetaToolsBase.__init__(self, user_id, original_input)

    # 调用ChatGPT完成对话
    def get_chatgpt_response(self, query: str):

        from dotenv import load_dotenv
        load_dotenv()
        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
        OPENAI_BASE_URL = os.environ['OPENAI_BASE_URL']
        OPENAI_MODEL = os.environ['OPENAI_MODEL']

        if OPENAI_MODEL == None or OPENAI_MODEL == "":
            OPENAI_MODEL = "gpt-3.5-turbo"

        model: ChatOpenAI

        prompt_str = "现在时间是：{now}。\
请分析指定内容的循环规则,输出循环规则和日期.\
循环规则格式:请选择以下几种输出格式进行输出：0是单次任务不循环,1是每天循环、2是每周循环、3是每月循环、4是每年循环;\
日期格式: 英文的星期几，或者几月几日，或者是几日.\
以下为返回格式示例。\
示例1: ('0', '2024-1-3'), 代表该输入无循环规则,仅2024年1月3日单次触发.\
示例2: ('1', 'NA'), 代表每天，无指定日期.\
示例3: ('2', 'monday'), 代表每周一.\
示例4: ('3', '18'), 代表每月18日.\
示例5: ('4', '1-3'), 代表每年1月3日.\
请开始分析以下内容的循环规则和日期：{topic}"

        prompt = ChatPromptTemplate.from_template(prompt_str)
        if OPENAI_BASE_URL != None and OPENAI_BASE_URL != "":
            model = ChatOpenAI(streaming=True, model_name=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, openai_api_base=OPENAI_BASE_URL, temperature=0.7, verbose=True)
        else:
            model = ChatOpenAI(streaming=True, model_name=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, temperature=0.7, verbose=True)
        output_parser = CommaSeparatedListOutputParser()

        chain = prompt | model | output_parser

        response = chain.invoke({"topic": query, "now": get_current_time()})

        print("================================")
        print(f"QuerRecurring response={response}")
        print("================================")

        return response

    def check_response(self, response: str):
        # 检查返回的字串是否符合要求
        try:
            params = ast.literal_eval(response)

            if len(params) < 2:
                print(f"查询循环规则失败：返回的参数个数少于要求:{response}")
                return False
            return True
        except Exception as e:
            print(f"查询循环规则失败: {str(e)}, input={response}")
            return False

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

    def _run(self, param: str) -> Any:
        logger.debug(f"=====================param={param}, userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")

        run_counter = 0
        user_input = param
        response = ""

        # try max 3 times
        while run_counter < 3:
            gpt_response = self.get_chatgpt_response(user_input)

            if self.check_response(gpt_response) == True:
                response = gpt_response
                print(f"===>>>final response={response}, type={type(response)}")
                break
            else:
                run_counter = run_counter + 1
        
        return response

if __name__ == "__main__":
    tool = QueryRecurring()
    result = tool.run("今年的父亲节是几号？")
    print(result)

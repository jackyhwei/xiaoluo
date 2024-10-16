import logging
from typing import Any
from datetime import datetime
from langchain.tools import BaseTool
import os
import ast
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseOutputParser

from .OddMetaTools import OddMetaToolsBase
from ...omengine.utils.datatime_utils import is_datestr_valid, get_current_time

logger = logging.getLogger(__name__)

class CommaSeparatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""

    def parse(self, text: str):
        """Parse the output of an LLM call."""

        return text.strip()

class QueryDate(BaseTool, OddMetaToolsBase):
    name = "QueryDate"
    description = "用于查询指定的日期，返回阳历日期和时间。示例:('2024-05-18', '19:15')" 

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

        now_time = get_current_time()
        # prompt_str = "现在时间是：" + now_time +"。请帮忙查询输入内容所对应的日期、星期几、中国农历日期，返回的数据里包含3个参数：阳历日期、星期几、农历日期。如：('2024-05-18', '星期六', '2024年四月廿五')。现在开始： {topic}"
        # prompt_str = "现在时间是：" + now_time +"。请帮忙查询输入内容所对应的日期、星期几、中国农历日期，返回的数据里包含3个参数：阳历日期、星期几、农历日期。如：('2024-05-18', '星期六', '2024年四月廿五')。返回前，先自行确认一下结果是否正确。现在开始： {topic}"
        # prompt_str = "现在时间是：" + now_time +"。请帮忙查询输入内容所对应的日期，返回日期。返回的日期格式示例：2024-05-18。现在开始： {topic}"
        # prompt_str = "现在时间是：" + now_time +"。请帮忙查询输入内容所对应的日期和时间。返回的日期格式示例：('2024-05-18', '19:15')。请省略你的推理过程，直接按示例格式输出经过你二次确认后的答案。现在开始：{topic}"
        prompt_str = "现在时间是：" + now_time +"。请帮忙查询下面输入内容所对应的日期和时间。返回的日期格式示例：('2024-05-18', '19:15')。现在开始查询：{topic}"

        prompt = ChatPromptTemplate.from_template(prompt_str)
        if OPENAI_BASE_URL != None and OPENAI_BASE_URL != "":
            model = ChatOpenAI(streaming=True, model_name=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, openai_api_base=OPENAI_BASE_URL, temperature=0.7, verbose=True)
        else:
            model = ChatOpenAI(streaming=True, model_name=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, temperature=0.7, verbose=True)
        output_parser = CommaSeparatedListOutputParser()

        chain = prompt | model | output_parser

        # FIXME 在前面的步骤里解析出来的参数经常就已经是一个错误的内容，因此使用原始问题去查询日期
        # response = chain.invoke({"topic": query})
        response = chain.invoke({"topic": OddMetaToolsBase._original_input})

        print(f"QuerDate response={response}")

        return response

    # def check_response3(self, response: str):
    #     # 检查返回的字串是否符合要求。返回的数据里包含3个参数：阳历日期、星期几、农历日期
    #     try:
    #         params = ast.literal_eval(response)
    #         print(f"check_response: len={len(params)}, response={response}")
    #         if len(params) != 3:
    #             return False
    #         else:
    #             return True
    #     except Exception as e:
    #         print(f"check_response error: {str(e)}, input={response}")
    #         return False

    def check_response(self, response: str):
        # 检查返回的字串是否符合要求：日期
        try:
            params = ast.literal_eval(response)
            if len(params) != 2:
                return False
            if is_datestr_valid(params[0], params[1]):
                return True
            else:
                return False
        except Exception as e:
            print(f"check_response error: {str(e)}, input={response}")
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
    tool = QueryDate()
    result = tool.run("今年的父亲节是几号？")
    print(result)

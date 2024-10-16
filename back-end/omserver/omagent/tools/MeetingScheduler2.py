import sqlite3
from typing import Any, Dict, Optional, Type, Union
import ast
import logging
import os
import json
from enum import Enum
from datetime import datetime

from langchain.schema import BaseOutputParser
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


from .QueryDate import QueryDate
from ...omengine.utils.datatime_utils import is_datestr_valid, OMRecurring, recurring_str_to_enum, get_current_time, get_weekday_list
from .OddMetaTools import OddMetaToolsBase
from .QueryRecurring import QueryRecurring

logger = logging.getLogger(__name__)

class CommaSeparatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""

    def parse(self, text: str):
        """Parse the output of an LLM call."""
        print(f"###########CommaSeparatedListOutputParser:{text}##########")
        return text.strip()

class MeetingSchedulerErr(Enum):
    NO_ERROR = 0
    ERR_INVALID_RECURRING = 1
    ERR_INVALID_MONTH_DAY = 2
    ERR_INVALID_YEAR_MONTH_DAY = 3
    ERR_INVALID_DAY = 4
    ERR_INVALID_WEEKAY = 5
    ERR_INVALID_TIME = 6
    ERR_OTHERS = 7

    def __str__(self):
        return self.name.title()

    def desc(value: int):
        map = {
            0: "参数校验通过",
            1: "无效的循环规则，有效参数包括有，0：单次任务不循环,1：每天循环、2：每周循环、3：每月循环、4：每年循环",
            2: "无效的日期参数-月日",
            3: "无效的日期参数-年月日",
            4: "无效的日期参数-日",
            5: "无效的日期参数-星期",
            6: "无效的时间参数，应为24小时制的时间",
            7: "无效参数",
        }

        return map.get(value, "无效的输入参数，重新检查输入参数")

class MeetingSchedulerInput(BaseModel):
    start_time: str = Field(description="24小时制的时间。如：'21:15'")
    recurring_type: int = Field(description="循环规则。0是单次任务不循环,1是每天循环、2是每周循环、3是每月循环、4是每年循环")
    title: str = Field(description="会议名称")
    attendees: str = Field(description="参与会议的人员")
#     schedule_date: str = Field(description="会议日期。\
# 英文的星期几，或者几月几日，或者是几日。\
# 当:\
# 循环规则是0时是年月日，\
# 循环规则是1时为NA，\
# 循环规则是2时为英文的星期几，\
# 循环规则是3时为日期，\
# 循环规则是4时为月日。\
# 以下为返回格式示例。\
# 示例1: ('0', '2024-1-3'), 代表该输入无循环规则,仅2024年1月3日单次触发.\
# 示例2: ('1', 'NA'), 代表每天，无指定日期.\
# 示例3: ('2', 'monday'), 代表每周一.\
# 示例4: ('3', '18'), 代表每月18日.\
# 示例5: ('4', '1-3'), 代表每年1月3日.")
    schedule_date: str = Field(description="会议日期")

class MeetingScheduler(BaseTool, OddMetaToolsBase):
    name = "MeetingScheduler"
    description = "用于预约会议。\
使用的时候需要接受5个内容：\
第1个是24小时制的时间；\
第2个是循环规则，0是不需要循环,1是每天循环、2是每周循环、3是每月循环、4是每年循环；\
第3个是会议名称。\
第4个是参与会议的人员。\
第5个是会议日期.\
如：('15:15', '2', '周例会', 'Jacky, Lucy', 'monday') 代表预约了一个每周星期一15点15分钟的周例会，参会人员包括Jacky, Lucy。"

#     description = "用于预约会议。\
# 使用的时候需要接受5个参数：\
# 第1个参数是24小时制的时间；\
# 第2个参数是循环规则，支持每天、每周、每月、每年、不循环；\
# 第3个参数是会议名称。\
# 第4个参数是参与会议的人员。\
# 第5个参数是会议日期;\
# 如：('15:15', '2', '周例会', 'Jacky, Lucy', 'monday') 代表预约了一个每周星期一15点15分钟的周例会，参会人员包括Jacky, Lucy。"


    # args_schema : Type[BaseModel] = MeetingSchedulerInput

    def __init__(self, user_id: int=0, original_input: str=None):
        super().__init__()
        OddMetaToolsBase.__init__(self, user_id, original_input)
        print(f"MeetingScheduler: userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")

    # async def _arun(self, start_time: str, recurring_type: int, title: str, attendees: str, schedule_date: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> Any:
    async def _arun(self, param: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

    # def _run(self, start_time: str, recurring_type: int, title: str, attendees: str, schedule_date: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
    def _run(self, param: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        logger.debug(f"=====================param={param}, userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")

        # XXX Qwen-7B-Chat llm might occationally return an invalid str like: 
        #   "('9:00', '每周星期一', '周例会', 'Jacky, Lucy, Cathy')\nObservation", 
        # we need to truncate it with \n to make it acceptable by literal_eval or eval.
        param = param[0:param.find('\n', 3)]
        params = ast.literal_eval(param)

        start_time = params[0]
        recurring_type = params[1]
        title = params[2]
        attendees = params[3]
        # schedule_date = params[4]

        ################################################
        repeat_day_of_week = ""
        repeat_month_day = ""

        calculated_date = ""
        recurring_type = OMRecurring.no_recurring.value

        user_id = OddMetaToolsBase._user_id
        original_input = OddMetaToolsBase._original_input

        # 1。check 循环规则是否解析正确
        error, recurring_type, repeat_day_of_week, repeat_month_day = \
            self.s1_verifyParam_RepeatRuleAndDay(recurring_type, params[4])
        if error != 0:
            error, repeat_month_day, repeat_day_of_week = self.s2_query_RepeatRuleAndDay(err=error, recurring_type=recurring_type, user_input=original_input)
            if error != MeetingSchedulerErr.NO_ERROR:
                return MeetingSchedulerErr.desc(error) # "会议预约失败：查询会议循环规则失败"

        # # 2。check 会议日期是否解析正确
        # error, repeat_day_of_week, repeat_month_day =  \
        #     self.verifyParam_Day(input_date=schedule_date, start_time=start_time, recurring_type=recurring_type)
        # if error != 0:
        #     return MeetingSchedulerErr.desc(error) # "预约会议失败：LLM未能正确识别并解析会议日期时间，请重新尝试"
    
        print(f"会议预约 - date={params[4]}: start_time={start_time},repeat_month_day={repeat_month_day}, repeat_day_of_week={repeat_day_of_week}")

        # 3。save to database
        conn = sqlite3.connect('db/db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO omserver_schedulesmodel \
                       (title, start_time, recurring_type, repeat_day_of_week, \
                        repeat_month_day, tool, user_id, \
                        attendees, original_input) \
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", \
                       (title, start_time, recurring_type, repeat_day_of_week, repeat_month_day, self.name, user_id, attendees, original_input))

        conn.commit()
        conn.close()
        result = "成功预约了会议。时间是：{date} {time}，主题是：{content}".format(date=calculated_date, time=start_time, content=title)

        # put_message(ChatMessage(type="user", user_name="sys", query="", role_name="agent", content=result, emote="neutral"))

        return result
    
    def step_1_query_recurringtype(self, query: str):
        # 手动查询用户输入中的日期及时间
        from dotenv import load_dotenv
        load_dotenv()
        LLM_API_KEY = os.environ.get('LLM_API_KEY', "")
        LLM_BASE_URLos.environ.get('LLMLLM_BASE_URL
        LLM_MODEL = os.environ.get('LLM_MODEL', "")

        if LLM_MODEL == None or LLM_MODEL == "":
            LLM_MODEL = "gpt-3.5-turbo"

        model: ChatOpenAI

#         prompt_str = "现在时间是：{now}。\
# 请分析指定内容的循环规则,输出json格式的循环规则和日期。\
# 其中，循环规则格式:请选择以下几种输出格式进行输出：0是单次任务不循环,1是每天循环、2是每周循环、3是每月循环、4是每年循环;\
# 日期格式: 英文的星期几，或者几月几日，或者是几日。\
# 以下为返回格式示例。\
# 示例1: (0, '2024-1-3'), 代表该输入无循环规则,仅2024年1月3日单次触发.\
# 示例2: (1, ''), 代表每天循环，无指定日期.\
# 示例3: (2, 'monday'), 代表每周一循环.\
# 示例4: (3, '18'), 代表每月18日循环.\
# 示例5: (4, '1-3'), 代表每年1月3日循环.\
# 请开始分析以下内容的循环规则和日期：{topic}"

        prompt_str = "现在时间是：{now}。\
请分析指定内容的循环规则,输出json格式循环规则。\
请选择0,1,2,3,4这几个数字来输出的循环规则，其中：0代表没有循环规则,1代表每天循环、2代表每周循环、3代表每月循环、4代表每年循环;\
请开始分析以下内容的循环规则和日期：{topic}"

        prompt = ChatPromptTemplate.from_template(prompt_str)
        if LLM_BASE_URL None and LLMLLM_BASE_URL:
            model = ChatOpenAI(streaming=True, model_name=LLM_MODEL, openai_api_key=LLM_API_KEY, openai_api_base=LLM_BASE_URLemperature=0.7, verbose=True)
        else:
            model = ChatOpenAI(streaming=True, model_name=LLM_MODEL, openai_api_key=LLM_API_KEY, temperature=0.7, verbose=True)
        output_parser = CommaSeparatedListOutputParser()

        chain = prompt | model | output_parser

        response = chain.invoke({"topic": query, "now": get_current_time()})

        print("================================")
        print(f"step_1_query_recurringtype_and_date={response}")
        print("================================")

        return response

    def step_2_query_date(self, query: str):
        # 手动查询用户输入中的日期及时间
        # 返回格式： ('2024-05-18', '19:15')

        load_dotenv()

        LLM_API_KEY = os.environ.get('LLM_API_KEY', "")
        LLM_BASE_URLos.environ.get('LLMLLM_BASE_URL
        LLM_MODEL = os.environ.get('LLM_MODEL', "")

        if LLM_MODEL == None or LLM_MODEL == "":
            LLM_MODEL = "gpt-3.5-turbo"

        model: ChatOpenAI

        now_time = get_current_time()
        # prompt_str = "现在时间是：" + now_time +"。请帮忙查询输入内容所对应的日期、星期几、中国农历日期，返回的数据里包含3个参数：阳历日期、星期几、农历日期。如：('2024-05-18', '星期六', '2024年四月廿五')。现在开始： {topic}"
        # prompt_str = "现在时间是：" + now_time +"。请帮忙查询输入内容所对应的日期、星期几、中国农历日期，返回的数据里包含3个参数：阳历日期、星期几、农历日期。如：('2024-05-18', '星期六', '2024年四月廿五')。返回前，先自行确认一下结果是否正确。现在开始： {topic}"
        # prompt_str = "现在时间是：" + now_time +"。请帮忙查询输入内容所对应的日期，返回日期。返回的日期格式示例：2024-05-18。现在开始： {topic}"
        # prompt_str = "现在时间是：" + now_time +"。请帮忙查询输入内容所对应的日期和时间。返回的日期格式示例：('2024-05-18', '19:15')。请省略你的推理过程，直接按示例格式输出经过你二次确认后的答案。现在开始：{topic}"
        prompt_str = "现在时间是：" + now_time +"。请帮忙查询下面输入内容所对应的日期和时间。返回格式示例：('2024-05-18', '19:15')。现在开始查询：{topic}"
        # llm响应
        # AIMessage(content="('2024-06-07', '19:00')" response_metadata={'finish_reason': 'stopstop'} id='run-52cb0d3a-291e-48e0-9e91-1ca1be1c69c4-0'）
        # llm响应2
        # AIMessage(content="根据您的输入，明天是2024年06月07日，晚上7点。因此，您的预约时间是('2024-06-07', '19:00')。", response_metadata={'finish_reason': 'stopstop'}, id='run-74dba77e-38e2-47a5-ad3e-0ee417d5c248-0')
        prompt_str = "现在时间是：" + now_time +"。请帮忙查询下面输入内容所对应的日期和时间。返回格式示例：('2024-05-18', '19:15')。现在开始查询：{topic}"

        prompt = ChatPromptTemplate.from_template(prompt_str)
        if LLM_BASE_URL None and LLMLLM_BASE_URL:
            model = ChatOpenAI(streaming=True, model_name=LLM_MODEL, openai_api_key=LLM_API_KEY, openai_api_base=LLM_BASE_URLemperature=0.7, verbose=True)
        else:
            model = ChatOpenAI(streaming=True, model_name=LLM_MODEL, openai_api_key=LLM_API_KEY, temperature=0.7, verbose=True)

        # output_parser = CommaSeparatedListOutputParser()
        # chain = prompt | model | output_parser
        chain = prompt | model

        from langchain_core.messages.ai import AIMessage
        r: AIMessage

        r = chain.invoke({"topic": query})

        print(f"step_2_query_date response={r}, type={type(r)}")

        return r.content

    def verifyParam_Day(self, recurring_type: int, input_date: str, start_time: str):
        print(f"verifyParam_Day: recurring_type={recurring_type}, input_date={input_date}, start_time={start_time}")
        user_id = OddMetaToolsBase._user_id
        original_input = OddMetaToolsBase._original_input

        error = 0
        repeat_month_day = ""
        repeat_day_of_week = ""

        # if recurring_type == 0:
        if recurring_type == OMRecurring.no_recurring.value:
            '''如果不是循环的任务，则需要查询一下具体的日期'''
            try:
                ''' 检查日期格式是否正确 '''
                repeat_month_day = datetime.strptime(input_date, '%Y-%m-%d')
                repeat_day_of_week = ""
            except Exception as e:
                logger.error(f"预约会议失败：查询日期失败，input={input_date}, recurring_type={recurring_type}, err={str(e)}")
                error = MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY.value
                repeat_day_of_week = ""
                repeat_month_day = input_date

            if error == MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY:
                '''如果日期格式不对，手动调用LLM查询一下具体的日期'''
                print(f"try use embeded tool to query date, input ={OddMetaToolsBase._original_input}")
                llm_resule = self.step_2_query_date(OddMetaToolsBase._original_input)
                print(f"llm result, input={llm_resule}")
                params = ast.literal_eval(llm_resule)
                if len(params) != 2:
                    print("预约会议失败：LLM未能正确识别并解析会议日期时间，请重新尝试")
                    error = MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY.value
                else:
                    input_date = params[0]
                    start_time = params[1]
                    print(f"input_date={input_date}, start_time={start_time}")
                    try:
                        repeat_month_day = datetime.strptime(input_date, '%Y-%m-%d')
                        repeat_day_of_week = ""
                        error = MeetingSchedulerErr.NO_ERROR
                    except Exception as e:
                        print(f"s2_query_RepeatRuleAndDay exceptin: {str(e)}")
                        error = MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY.value

            if error == MeetingSchedulerErr.NO_ERROR:
                '''若是日期格式正常，再补充检查时间格式是否正确'''
                try:
                    # 检查日期+时间格式是否正确
                    if is_datestr_valid(input_date_str=input_date, input_time_str=start_time) == False:
                        logger.error(f"预约会议失败：查询日期失败，input={input_date}, recurring_type={recurring_type}, start_time={start_time}, err={str(e)}")
                        error = MeetingSchedulerErr.ERR_INVALID_TIME.value
                except Exception as e:
                    logger.error(f"预约会议失败：查询日期失败，input={input_date}, recurring_type={recurring_type}, err={str(e)}")
                    error = MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY.value
                    repeat_month_day = input_date
                    repeat_day_of_week = ""
            
        elif recurring_type == OMRecurring.weekly.value:
            weekdays = get_weekday_list()
            if not input_date in weekdays:
                 error = MeetingSchedulerErr.ERR_INVALID_WEEKAY.value
            else:
                repeat_day_of_week = input_date
                repeat_month_day = ""
        elif recurring_type == OMRecurring.monthly.value:
            try:
                repeat_month_day = datetime.strptime(input_date, '%d')
                repeat_day_of_week = ""
            except Exception as e:
                logger.error(f"预约会议失败：查询日期失败，input={input_date}, recurring_type={recurring_type}, err={str(e)}")
                error = MeetingSchedulerErr.ERR_INVALID_DAY.value
        elif recurring_type == OMRecurring.yearly.value:
            try:
                repeat_month_day = datetime.strptime(input_date, '%m-%d')
                repeat_day_of_week = ""
            except Exception as e:
                logger.error(f"预约会议失败：查询日期失败，input={input_date}, recurring_type={recurring_type}, err={str(e)}")
                error = MeetingSchedulerErr.ERR_INVALID_MONTH_DAY.value
        else:
            error = MeetingSchedulerErr.ERR_OTHERS.value
        
        return error, repeat_month_day, repeat_day_of_week

    def s2_query_RepeatRuleAndDay(self, err: int, recurring_type: int, user_input: str):
        '''
        函数: s2_query_RepeatRuleAndDay
        参数: err: int, recurring_type: int, user_input: str
        返回: error, month_day, week_day
        '''
        error = MeetingSchedulerErr.NO_ERROR
        month_day = ""
        week_day = ""

        if err == MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY.value:
            pass
        elif err == MeetingSchedulerErr.ERR_INVALID_MONTH_DAY.value:
            pass
        elif err == MeetingSchedulerErr.ERR_INVALID_DAY.value:
            pass
        elif err == MeetingSchedulerErr.ERR_INVALID_WEEKAY.value:
            pass
        else:
            pass

        return error, month_day, week_day

    def s1_verifyParam_RepeatRuleAndDay(self, recurring_type: int, schedule_date: str):
        error = 0
        input_date = schedule_date
        repeat_day_of_week = ""
        repeat_month_day = ""

        if recurring_type < 0 or recurring_type > 4:
            error = MeetingSchedulerErr.ERR_INVALID_RECURRING.value
        else:
            if recurring_type == 0:
                try:
                    repeat_month_day = datetime.strptime(input_date, '%Y-%m-%d')
                    repeat_day_of_week = ""
                except Exception as e:
                    print(f"invalid date str: {input_date}, error desc: {str(e)}")
                    error = MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY.value
            elif recurring_type == 1:
                # daily
                repeat_month_day = "NA"
                repeat_day_of_week = ""
            elif recurring_type == 2:
                # weekly
                try:
                    # week_day = today.strftime("%A")
                    week_day_zh = {
                        "monday": "星期一",
                        "tuesday": "星期二",
                        "wednesday": "星期三",
                        "thursday": "星期四",
                        "friday": "星期五",
                        "saturday": "星期六",
                        "sunday": "星期日",
                    }
                    if not input_date.lower() in week_day_zh:
                        error = MeetingSchedulerErr.ERR_INVALID_WEEKAY.value
                    else:
                        repeat_day_of_week = input_date.lower()
                        repeat_month_day = ""
                except Exception as e:
                    print(f"invalid week day: {input_date}, error desc: {str(e)}")
                    error = MeetingSchedulerErr.ERR_INVALID_WEEKAY.value
            elif recurring_type == 3:
                # monthly
                try:
                    day = int(input_date)
                    repeat_month_day = day
                    repeat_day_of_week = ""
                except Exception as e:
                    print(f"invalid day of month str: {input_date}, error desc: {str(e)}")
                    error = MeetingSchedulerErr.ERR_INVALID_DAY.value
            elif recurring_type == 4:
                # yearly
                try:
                    repeat_month_day = datetime.strptime(input_date, '%m-%d')
                    repeat_day_of_week = ""
                except Exception as e:
                    print(f"invalid month day: {input_date}, error desc: {str(e)}")
                    error = MeetingSchedulerErr.ERR_INVALID_MONTH_DAY.value
            else:
                print(f"invalid recurring type: {recurring_type}")
                error = MeetingSchedulerErr.ERR_INVALID_RECURRING.value
        
        return error, recurring_type, repeat_day_of_week, repeat_month_day


    # start_time: str = Field(description="24小时制的时间。如：'21:15'")
    # recurring_type: int = Field(description="循环规则。0是单次任务不循环,1是每天循环、2是每周循环、3是每月循环、4是每年循环")
    # title: str = Field(description="会议名称")
    # attendees: str = Field(description="参与会议的人员")
    # schedule_date: str = Field(description="会议日期")

    def _run2(self, param:str) -> str:
        logger.debug(f"=====================param={param}, userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")

        # XXX Qwen-7B-Chat llm might occationally return an invalid str like: 
        #   "('9:00', '每周星期一', '周例会', 'Jacky, Lucy, Cathy')\nObservation", 
        # we need to truncate it with \n to make it acceptable by literal_eval or eval.
        param = param[0:param.find('\n', 3)]

        params = ast.literal_eval(param)

        # 检查LLM返回的参数数量
        if len(params) != 5:
            return "预约会议失败：对不起，信息不足，您需要告知日期、时间、循环规则和事项才能为您记录此任务，请重新尝试"

        input_date = params[0]
        start_time = params[1]
        recurring_type = params[2]
        title = params[3]
        attendees = params[4]

        repeat_day_of_week = ""
        repeat_month_day = ""

        print(f"langchain parsed param: input_date={input_date}, start_time={start_time}, recurring_type={recurring_type}, title={title}, attendees={attendees}")

        # calculated_date = ""
        # recurring_type = OMRecurring.no_recurring.value

        user_id = OddMetaToolsBase._user_id
        original_input = OddMetaToolsBase._original_input

        # 1。废弃langchain解析的结果，自己手动查询循环规则及日期
        result = self.step_1_query_recurringtype(query=original_input)
        print(f"step_1_query_recurringtype_and_date result={result}")
        # params = ast.literal_eval(result)
        # if len(params) != 2:
        #     return "会议预约失败1：查询会议循环规则失败，请重新尝试"
        # recurring_type = params[0]
        # schedule_date = param[1]
        # print(f"step_1_query_recurringtype_and_date result after parse, recurring_type={recurring_type}, schedule_date={schedule_date}")
        recurring_type = result

        # # 2。check 循环规则是否解析正确
        # error, recurring_type, repeat_day_of_week, repeat_month_day = \
        #     self.verifyParam_RepeatRuleAndDay(recurring_type=recurring_type, schedule_date=schedule_date)
        # if error != 0:
        #     return "会议预约失败2：查询会议循环规则失败，请重新尝试"

        # 3。废弃langchain解析结果，手动查询日期
        result = self.step_2_query_date(query=original_input)

        error, repeat_month_day, repeat_day_of_week =  \
            self.verifyParam_Day(input_date=input_date, start_time=start_time, recurring_type=recurring_type)
        if error != 0:
            return "预约会议失败：LLM未能正确识别并解析会议日期时间，请重新尝试"
    
        print(f"会议预约 - date={input_date}: start_time={start_time},repeat_month_day={repeat_month_day}, repeat_day_of_week={repeat_day_of_week}")

        # 5。save to database
        conn = sqlite3.connect('db/db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO omserver_schedulesmodel \
                       (title, start_time, recurring_type, repeat_day_of_week, \
                        repeat_month_day, tool, user_id, \
                        attendees, original_input) \
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", \
                       (title, start_time, recurring_type, repeat_day_of_week, repeat_month_day, self.name, user_id, attendees, original_input))

        conn.commit()
        conn.close()
        result = "成功预约了会议。时间是：{date} {time}，主题是：{content}".format(date=repeat_month_day, time=start_time, content=title)

        # put_message(ChatMessage(type="user", user_name="sys", query="", role_name="agent", content=result, emote="neutral"))

        return result

if __name__ == "__main__":
    calculator_tool = MeetingScheduler()
    input = "帮我预约一个今天晚上7点的项目会议，邀请Jacky和顾振华参加"
    input = "帮我预约一个明天晚上7点的项目会议，邀请Jacky和Jason参加"
    input = "帮我预约一个每周三上午9点半的周例会，邀请Jacky和Lucy参加"
    input = "帮我预约一个每月10号中午12点半的月度会议，邀请Jacky, Lucy, Cathy参加"
    input = "帮我预约一个每年11月25日晚上20点半的年度会议，邀请Jacky, Lucy, Cathy参加"
    result = calculator_tool.run(input)
    print(result)

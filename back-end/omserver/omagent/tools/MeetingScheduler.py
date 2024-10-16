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
            4: "无效的日期参数-正确的值应是数字的每月第几日",
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
    description = "用于预约会议，闹钟，待办，日程，提醒等。\
使用的时候需要接受5个内容：\
第1个是24小时制的时间；\
第2个是循环规则，0是不需要循环,1是每天循环、2是每周循环、3是每月循环、4是每年循环；\
第3个是会议名称。\
第4个是参与会议的人员。\
第5个是会议日期.\
如：('15:15', '2', '周例会', 'Jacky, Lucy', '星期一') 代表预约了一个每周星期一15点15分钟的周例会，参会人员包括Jacky, Lucy。"

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

    async def _arun(self, param: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

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
        input_date = params[4]

        ################################################
        repeat_day_of_week = ""
        repeat_month_day = ""

        user_id = OddMetaToolsBase._user_id
        original_input = OddMetaToolsBase._original_input

        print(f"STEP 0: recurring={recurring_type}, date={input_date}, time={start_time}, repeat_day_of_week={repeat_day_of_week}, repeat_month_day={repeat_month_day}, title={title}, attendees={attendees}")

        # 检查循环规则是否正常，若循环规则参数的类型都解析错误了，直接返回
        try:
            recurring_type = int(recurring_type)
        except Exception as e:
            logger.error(f"invalid recurring_type={recurring_type}, re-try to parse recurring type parameter")
            return "循环规则参数解析错误，请重新尝试解析循环规则参数，然后再做尝试"

        # 1。check 循环规则是否解析正确
        error, recurring_type, repeat_day_of_week, repeat_month_day = \
            self.s1_verifyParam_RepeatRuleAndDay(recurring_type, input_date)
        
        print(f"STEP 1: error={error},recurring_type={recurring_type}, repeat_day_of_week={repeat_day_of_week}, repeat_month_day={repeat_month_day}")

        # 2。如果Langchain自动解析出来的参数存在问题，尝试手动用LLM去查询解析一下
        if error != MeetingSchedulerErr.NO_ERROR.value:
            error, repeat_month_day, repeat_day_of_week, start_time = self.s2_query_RepeatRuleAndDay(err=error, recurring_type=recurring_type, input_date=input_date, input_time=start_time, user_input=original_input)
        
        print(f"STEP 2: error={error},recurring_type={recurring_type}, repeat_day_of_week={repeat_day_of_week}, repeat_month_day={repeat_month_day}")

        # 3。如果手动解析的结果还是不正确，返回失败
        if error != MeetingSchedulerErr.NO_ERROR.value:
            return MeetingSchedulerErr.desc(error) # "会议预约失败：查询会议循环规则失败"
    
        logger.debug(f"会议预约 - date={input_date}: start_time={start_time},repeat_month_day={repeat_month_day}, repeat_day_of_week={repeat_day_of_week}")

        # 4。解析出来的参数校验通过，保存到数据库 
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
        result = "成功预约了会议。时间是：{date} {time}，主题是：{content}，参会人员：{attendees}".format(date=repeat_month_day, time=start_time, content=title, attendees=attendees)

        # put_message(RealtimeMessage(type="user", user_name="sys", query="", role_name="agent", content=result, emote="neutral"))

        return result

    def query_day(self, query: str):
        ''' monthly, 查询用户输入中的每月第几日的信息
        如：每月15日，则返回格式： ('15')
        '''
        load_dotenv()

        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
        OPENAI_BASE_URL = os.environ['OPENAI_BASE_URL']
        OPENAI_MODEL = os.environ['OPENAI_MODEL']

        if OPENAI_MODEL == None or OPENAI_MODEL == "":
            OPENAI_MODEL = "gpt-3.5-turbo"

        model: ChatOpenAI

        now_time = get_current_time()
        prompt_str = "现在时间是：" + now_time +"。请帮忙查询下面输入内容里包含的每月的第几日。返回格式示例：('15')。现在开始查询：{topic}"

        prompt = ChatPromptTemplate.from_template(prompt_str)
        if OPENAI_BASE_URL != None and OPENAI_BASE_URL != "":
            model = ChatOpenAI(streaming=True, model_name=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, openai_api_base=OPENAI_BASE_URL, temperature=0.7, verbose=True)
        else:
            model = ChatOpenAI(streaming=True, model_name=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, temperature=0.7, verbose=True)

        # output_parser = CommaSeparatedListOutputParser()
        # chain = prompt | model | output_parser
        chain = prompt | model

        from langchain_core.messages.ai import AIMessage
        r: AIMessage

        r = chain.invoke({"topic": query})

        print(f"query_yearmonthday response={r}, type={type(r)}")

        return r.content

    def query_monthday(self, query: str):
        ''' Yearly, 查询用户输入中的每年的几月几日信息
        如：每年的12月15日，则返回格式： ('12','15')
        '''
        load_dotenv()

        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
        OPENAI_BASE_URL = os.environ['OPENAI_BASE_URL']
        OPENAI_MODEL = os.environ['OPENAI_MODEL']

        if OPENAI_MODEL == None or OPENAI_MODEL == "":
            OPENAI_MODEL = "gpt-3.5-turbo"

        model: ChatOpenAI

        now_time = get_current_time()
        prompt_str = "现在时间是：" + now_time +"。请帮忙查询下面输入内容里包含的每年的几月几日。返回格式示例：('12-15')。现在开始查询：{topic}"

        prompt = ChatPromptTemplate.from_template(prompt_str)
        if OPENAI_BASE_URL != None and OPENAI_BASE_URL != "":
            model = ChatOpenAI(streaming=True, model_name=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, openai_api_base=OPENAI_BASE_URL, temperature=0.7, verbose=True)
        else:
            model = ChatOpenAI(streaming=True, model_name=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, temperature=0.7, verbose=True)

        # output_parser = CommaSeparatedListOutputParser()
        # chain = prompt | model | output_parser
        chain = prompt | model

        from langchain_core.messages.ai import AIMessage
        r: AIMessage

        r = chain.invoke({"topic": query})

        print(f"query_yearmonthday response={r}, type={type(r)}")

        return r.content
    def query_yearmonthday(self, query: str):
        # 手动查询用户输入中的日期及时间
        # 返回格式： ('2024-05-18', '19:15')

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
        prompt_str = "现在时间是：" + now_time +"。请帮忙查询下面输入内容所对应的日期和时间。返回格式示例：('2024-05-18', '19:15')。现在开始查询：{topic}"
        # llm响应
        # AIMessage(content="('2024-06-07', '19:00')" response_metadata={'finish_reason': 'stopstop'} id='run-52cb0d3a-291e-48e0-9e91-1ca1be1c69c4-0'）
        # llm响应2
        # AIMessage(content="根据您的输入，明天是2024年06月07日，晚上7点。因此，您的预约时间是('2024-06-07', '19:00')。", response_metadata={'finish_reason': 'stopstop'}, id='run-74dba77e-38e2-47a5-ad3e-0ee417d5c248-0')
        prompt_str = "现在时间是：" + now_time +"。请帮忙查询下面输入内容里包含的日期和时间信息。返回格式示例：('2024-05-18', '19:15')。现在开始查询：{topic}"

        prompt = ChatPromptTemplate.from_template(prompt_str)
        if OPENAI_BASE_URL != None and OPENAI_BASE_URL != "":
            model = ChatOpenAI(streaming=True, model_name=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, openai_api_base=OPENAI_BASE_URL, temperature=0.7, verbose=True)
        else:
            model = ChatOpenAI(streaming=True, model_name=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY, temperature=0.7, verbose=True)

        # output_parser = CommaSeparatedListOutputParser()
        # chain = prompt | model | output_parser
        chain = prompt | model

        from langchain_core.messages.ai import AIMessage
        r: AIMessage

        r = chain.invoke({"topic": query})

        print(f"query_yearmonthday response={r}, type={type(r)}")

        return r.content

    def s2_query_RepeatRuleAndDay(self, err: int, recurring_type: int, input_date: str, input_time: str, user_input: str):
        '''
        函数: s2_query_RepeatRuleAndDay
        参数: err: int, recurring_type: int, user_input: str
        返回: error, month_day, week_day
        '''
        error = MeetingSchedulerErr.NO_ERROR.value
        month_day = ""
        week_day = ""
        start_time = input_time

        if err == MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY.value:
            '''如果不是循环的任务，手动调用LLM查询一下具体的年月日信息'''
            try:
                ''' 检查日期格式是否正确 '''
                month_day = datetime.strptime(input_date, '%Y-%m-%d')
                week_day = ""
            except Exception as e:
                logger.error(f"预约会议失败：查询日期失败，input={input_date}, recurring_type={recurring_type}, err={str(e)}")
                error = MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY.value
                week_day = ""
                month_day = input_date

            if error == MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY.value:
                '''如果日期格式不对，手动调用LLM查询一下具体的日期'''
                print(f"try use embeded tool to query date, input ={OddMetaToolsBase._original_input}")
                llm_resule = self.query_yearmonthday(OddMetaToolsBase._original_input)
                print(f"llm result, input={llm_resule}")
                params = ast.literal_eval(llm_resule)
                if len(params) != 2:
                    print("预约会议失败：LLM未能正确识别并解析会议日期时间，请重新尝试")
                    error = MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY.value
                else:
                    input_date = params[0]
                    start_time = params[1]
                    print(f"input_date={input_date}, re-calced start_time={start_time}, input start_time={input_time}")
                    try:
                        test_month_day = datetime.strptime(input_date, '%Y-%m-%d')
                        month_day = input_date
                        week_day = ""
                        error = MeetingSchedulerErr.NO_ERROR.value
                    except Exception as e:
                        print(f"s2_query_RepeatRuleAndDay exceptin: {str(e)}")
                        error = MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY.value

            if error == MeetingSchedulerErr.NO_ERROR.value:
                '''若是日期格式正常，再补充检查时间格式是否正确'''
                try:
                    # 检查日期+时间格式是否正确
                    if is_datestr_valid(input_date_str=input_date, input_time_str=start_time) == False:
                        logger.error(f"预约会议失败：查询日期失败，input={input_date}, recurring_type={recurring_type}, start_time={start_time}, err={str(e)}")
                        error = MeetingSchedulerErr.ERR_INVALID_TIME.value
                except Exception as e:
                    logger.error(f"预约会议失败：查询日期失败，input={input_date}, recurring_type={recurring_type}, err={str(e)}")
                    error = MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY.value
                    month_day = input_date
                    week_day = ""

        elif err == MeetingSchedulerErr.ERR_INVALID_MONTH_DAY.value:
            '''如果每年的第几月第几日解析不对，手动调用LLM查询一下具体的日子'''
            try:
                print(f"try use embeded tool to query month and day of year, input ={OddMetaToolsBase._original_input}")
                llm_resule = self.query_monthday(OddMetaToolsBase._original_input)
                print(f"llm result, input={llm_resule}")
                new_input_date = ast.literal_eval(llm_resule)
                print(f"input_date={input_date}, llm result={new_input_date}")
                try:
                    test_month_day = datetime.strptime(new_input_date, '%m-%d')
                    month_day = new_input_date
                    week_day = ""
                    error = MeetingSchedulerErr.NO_ERROR.value
                except Exception as e:
                    print(f"s2_query_RepeatRuleAndDay exceptin: {str(e)}")
                    error = MeetingSchedulerErr.ERR_INVALID_MONTH_DAY.value
            except Exception as e:
                logger.error(f"input_date={input_date}, error={str(e)}")
                error = MeetingSchedulerErr.ERR_INVALID_MONTH_DAY.value

        elif err == MeetingSchedulerErr.ERR_INVALID_DAY.value:
            '''如果每月第几日解析不对，手动调用LLM查询一下具体的日子'''
            try:
                print(f"try use embeded tool to query day of month, input ={OddMetaToolsBase._original_input}")
                new_input_date = self.query_day(OddMetaToolsBase._original_input)
                print(f"input_date={input_date}, llm result={new_input_date}")
                try:
                    test_day = int(new_input_date)
                    month_day = new_input_date
                    week_day = ""
                    error = MeetingSchedulerErr.NO_ERROR.value
                except Exception as e:
                    print(f"s2_query_RepeatRuleAndDay exceptin: {str(e)}")
                    error = MeetingSchedulerErr.ERR_INVALID_DAY.value
            except Exception as e:
                logger.error(f"input_date={input_date}, error={str(e)}")
                error = MeetingSchedulerErr.ERR_INVALID_DAY.value

        elif err == MeetingSchedulerErr.ERR_INVALID_WEEKAY.value:
            pass
        else:
            pass

        return error, month_day, week_day, start_time

    def s1_verifyParam_RepeatRuleAndDay(self, recurring_type: int, schedule_date: str):
        error = MeetingSchedulerErr.NO_ERROR.value
        input_date = schedule_date
        repeat_day_of_week = ""
        repeat_month_day = ""

        if recurring_type < 0 or recurring_type > 4:
            error = MeetingSchedulerErr.ERR_INVALID_RECURRING.value
        else:
            if recurring_type == OMRecurring.no_recurring.value:
                try:
                    repeat_month_day = datetime.strptime(input_date, '%Y-%m-%d')
                    repeat_day_of_week = ""
                except Exception as e:
                    logger.error(f"invalid date str: {input_date}, error desc: {str(e)}")
                    error = MeetingSchedulerErr.ERR_INVALID_YEAR_MONTH_DAY.value
            elif recurring_type == OMRecurring.daily.value:
                # daily
                repeat_month_day = "NA"
                repeat_day_of_week = ""
            elif recurring_type == OMRecurring.weekly.value:
                # weekly
                try:
                    # week_day = today.strftime("%A")
                    week_day_en = {  
                        "星期一": "Monday",  
                        "星期二": "Tuesday",  
                        "星期三": "Wednesday",  
                        "星期四": "Thursday",  
                        "星期五": "Friday",  
                        "星期六": "Saturday",  
                        "星期日": "Sunday",  
                    } 
                    
                    if not input_date in week_day_en:
                        error = MeetingSchedulerErr.ERR_INVALID_WEEKAY.value
                    else:
                        repeat_day_of_week = week_day_en.get(input_date).lower()
                        repeat_month_day = ""
                except Exception as e:
                    logger.error(f"invalid week day: {input_date}, error desc: {str(e)}")
                    error = MeetingSchedulerErr.ERR_INVALID_WEEKAY.value
            elif recurring_type == OMRecurring.monthly.value:
                # monthly
                try:
                    day = int(input_date)
                    repeat_month_day = day
                    repeat_day_of_week = ""
                except Exception as e:
                    logger.error(f"invalid day of month str: {input_date}, error desc: {str(e)}")
                    error = MeetingSchedulerErr.ERR_INVALID_DAY.value
            elif recurring_type == OMRecurring.yearly.value:
                # yearly
                try:
                    repeat_month_day = datetime.strptime(input_date, '%m-%d')
                    repeat_day_of_week = ""
                except Exception as e:
                    logger.error(f"invalid month day: {input_date}, error desc: {str(e)}")
                    error = MeetingSchedulerErr.ERR_INVALID_MONTH_DAY.value
            else:
                logger.error(f"invalid recurring type: {recurring_type}")
                error = MeetingSchedulerErr.ERR_INVALID_RECURRING.value
        
        return error, recurring_type, repeat_day_of_week, repeat_month_day


if __name__ == "__main__":
    calculator_tool = MeetingScheduler()
    input = "帮我预约一个今天晚上7点的项目会议，邀请Jacky和CC参加"
    input = "帮我预约一个明天下午3点的项目会议，邀请Jacky和Jason参加"
    input = "帮我预约一个后天晚上9点的项目会议，邀请Jacky和Cathy参加"
    input = "帮我预约一个一小时后的项目会议，邀请Jacky和Selina参加"
    input = "帮我订一个每天上午9点半的晨会，邀请Jacky和Lucy参加"
    input = "帮我预约一个每周三上午9点半的周例会，邀请Jacky和Lucy参加"
    input = "帮我预约一个每月10号中午12点半的月度会议，邀请Jacky, Lucy, Cathy参加"
    input = "帮我预约一个每年11月25日晚上20点半的年度会议，邀请Jacky, Lucy, Cathy, Selina, CC参加"
    result = calculator_tool.run(input)
    print(result)

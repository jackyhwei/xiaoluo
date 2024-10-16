import sqlite3
from typing import Any
import ast
import logging
from datetime import datetime
from langchain.tools import BaseTool

from .QueryDate import QueryDate
from ...omengine.utils.datatime_utils import is_datestr_valid, OMRecurring
from .OddMetaTools import OddMetaToolsBase
from .QueryRecurring import QueryRecurring

logger = logging.getLogger(__name__)

class ScheduleAdder(BaseTool, OddMetaToolsBase):
    name = "ScheduleAdder"
    # description = "用于设置闹钟、日程、待办任务,使用的时候需要接受3个参数，第1个参数是时间,第2个参数是以周为单位的循环规则（如:'0101010'代表每周二、周四和周六循环，'0000000'代表不循环），第3个参数代表要执行的事项,如：('15:15', '0000001', '提醒主人叫奶茶')代表每周日15点15分钟提醒主人叫奶茶"
    # description = "用于设置闹钟、日程、待办任务。使用的时候需要接受3个参数：第1个参数是时间；第2个参数是循环规则，支持每天、每周、每月、每年，若不循环则指定日期闹钟任务待办的具体日期；第3个参数代表要执行的事项。如：('15:15', '每周星期天', '提醒主人叫奶茶')代表每周的星期天15点15分钟提醒主人叫奶茶。"
#     description = "用于设置闹钟、日程、待办任务。\
# 使用的时候需要接受4个参数:\
# 第1个参数是日期;\
# 第2个参数是时间;\
# 第3个参数是循环规则,支持每天、每周、每月、每年、不循环；\
# 第4个参数代表要执行的事项。\
# 注意:第1个参数只有在第3个参数不是'不循环'时有值,否则为空\
# 如：('', '15:15', '每周星期天', '提醒主人叫奶茶')代表每周的星期天15点15分钟提醒主人叫奶茶。"

#     description = "用于设置闹钟、日程、待办任务。\
# 使用的时候需要接受4个参数:\
# 第1个参数是对应的日期;\
# 第2个参数是对应的时间;\
# 第3个参数是循环规则,支持 每天、每周、每月、每年和不循环，且只能是这5个选项中的一个；\
# 第4个参数代表要执行的事项。\
# 注意:第1个参数只有在第3个参数的值是不循环时才有值,否则为空。\
# 如：('星期天', '15:15', '每周', '提醒主人叫奶茶')代表每周的星期天15点15分钟提醒主人叫奶茶。"

    description = "用于设置闹钟、日程、待办任务。\
使用的时候需要接受4个参数:\
第1个参数是闹钟的日期;\
第2个参数是闹钟的时间;\
第3个参数是循环规则,支持每天、每周、每月、每年或者是具体的日期；\
第4个参数代表要执行的事项。\
注意:第1个参数只有当第3个参数的值不是具体的日期时才有值,否则为''。\
如：('2024-6-26', '21:15', '2024-6-26', '提醒主人叫奶茶')代表2024-6-26的21点15分钟提醒主人叫奶茶。"

    description = "用于设置闹钟、日程、待办任务。\
使用的时候需要接受4个参数：\
第1个参数是闹钟日期;\
第2个参数是24小时制的时间；\
第3个参数是循环规则，支持每天、每周、每月、每年、不循环；\
第4个参数是闹钟的事项。\
注意：第一个参数只有在第3个参数存在循环规则时有值，否则为空.\
如：('星期天', '15:15', '每周', '提醒主人叫奶茶')代表每周的星期天15点15分钟提醒主人叫奶茶。"

    def __init__(self, user_id: int=0, original_input: str=None):
        super().__init__()
        OddMetaToolsBase.__init__(self, user_id, original_input)
        print(f"ScheduleAdder: userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

    def _run(self, param:str) -> str:
        logger.debug(f"=====================param={param}, userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")

        # XXX Qwen-7B-Chat llm might occationally return an invalid str like: 
        #   "('9:00', '每周星期一', '周例会', 'Jacky, Lucy, Cathy')\nObservation", 
        # we need to truncate it with \n to make it acceptable by literal_eval or eval.
        param = param[0:param.find('\n', 3)]
        params = ast.literal_eval(param)

        if len(params) != 4:
            return "对不起，信息不足，您需要告知日期、时间、循环规则和事项才能为您记录此任务，请重新尝试"

        title = params[3]
        start_time = params[1]
        input_repeat_rule = params[2]
        attendees = params[4]

        input_date = params[0]

        repeat_day_of_week = ""
        repeat_month_day = ""

        user_id = OddMetaToolsBase._user_id
        original_input = OddMetaToolsBase._original_input

        calculated_date = ""
        recurring_type = OMRecurring.no_recurring.value

        # Qwen-7B-Chat返回的循环规则也总是不对，调用QueryLoopType将手动检测循环规则
        print(f"STEP 1: try call QueryRepeatRule tool to re-estimate repeat rule")
        try:
            tool = QueryRecurring(user_id=user_id, original_input=original_input)
            recurring_type = tool.run(original_input)
            print(f"查询循环规则: input={original_input}, output={recurring_type}")
        except Exception as e:
            logger.error(f"查询循环规则：失败。input={original_input}, err={str(e)}")
            recurring_type = OMRecurring.no_recurring.value
        print(f"repeat rule={input_repeat_rule}:{recurring_type}")

        # Qwen-7B-Chat返回的日期总是不对，调用QueryDate将日期转换成我要的格式
        print(f"STEP 2: try call QueryDate tool to convert date str to a formated date str")
        if recurring_type == OMRecurring.no_recurring.value or recurring_type == OMRecurring.yearly.value:
            try:
                tool = QueryDate(user_id=user_id, original_input=original_input)
                calculated_date = tool.run(input_date)
                print(f"查询日期: input={input_date}, output={calculated_date}")
            except Exception as e:
                logger.error(f"查询日期失败：input={input_date}, err={str(e)}")
                calculated_date = input_date
        elif recurring_type == OMRecurring.monthly.value:
            pass
        else:
            pass
    
        print(f"date={input_date}:{calculated_date}")


        try:
            print("adding a new schedule")
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
            print("added a new schedule")
            result = "日程设置成功。时间是：{date} {time}，主题是：{content}".format(date=calculated_date, time=start_time, content=title)
        except Exception as e:
            logger.exception(f"新增日程安排失败，请重新尝试: {str(e)}")
            result = "新增日程安排失败，请重新尝试"

        # put_message(ChatMessage(type="user", user_name="sys", query="", role_name="agent", content=result, emote="neutral"))

        return result

if __name__ == "__main__":
    calculator_tool = ScheduleAdder()
    query = "请帮忙设置一个明天上午9点35分的闹钟，提醒我买宅男快活水"
    query = "请帮忙设置一个闹钟，提醒我每周五晚上7点15分买奶茶"
    query = "请帮忙设置一个每月10日晚上8点15分的闹钟，提醒我发钱了"
    query = "请帮忙设置一个每年11月25日晚上8点45分的闹钟，提醒我party要开始了"
    result = calculator_tool.run(query)
    print(result)

from datetime import datetime
import os
import pytz
import time
from enum import Enum

TIMEZONE = os.environ.get("TIMEZONE","Asia/Shanghai")

class OMRecurring(Enum):
    no_recurring = 0
    daily = 1
    weekly = 2
    monthly = 3
    yearly = 4

    def __str__(self):
        return self.name.title()
    
    def print(self):
        print(OMRecurring.no_recurring)      # 输出: OMRecurring.No_Recurring
        print(OMRecurring.monthly.value)     # 输出: 3
        print(str(OMRecurring.yearly))       # 输出: Yearly

def recurring_str_to_enum(input: str):
    if input.lower() == str(OMRecurring.yearly).lower():
        return OMRecurring.yearly.value
    if input.lower() == str(OMRecurring.monthly).lower():
        return OMRecurring.monthly.value
    if input.lower() == str(OMRecurring.weekly).lower():
        return OMRecurring.weekly.value
    if input.lower() == str(OMRecurring.daily).lower():
        return OMRecurring.daily.value
    
    return OMRecurring.no_recurring.value

def get_current_time_str():
    current_time = datetime.now(pytz.timezone(TIMEZONE))
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time

def get_current_time() -> str:
    # 获取当前时间
    now = datetime.now()
        # 获取当前日期
    today = now.date()
    # 获取星期几的信息
    week_day = today.strftime("%A")
    # 将星期几的英文名称转换为中文
    week_day_zh = {
        "Monday": "星期一",
        "Tuesday": "星期二",
        "Wednesday": "星期三",
        "Thursday": "星期四",
        "Friday": "星期五",
        "Saturday": "星期六",
        "Sunday": "星期日",
    }.get(week_day, "未知")
    # 将日期格式化为字符串
    date_str = today.strftime("%Y年%m月%d日")
    
    # 将时间格式化为字符串
    time_str = now.strftime("%H:%M")

    return "{0} {1} {2}".format(time_str, week_day_zh, date_str)

def is_datestr_valid(input_date_str: str, input_time_str: str):
    current_time = datetime.now()
    current_time_str = current_time.strftime('%Y-%m-%d %H:%M')
    current_time = datetime.strptime(current_time_str, '%Y-%m-%d %H:%M')

    input_date = ""
    input_time = ""

    if input_date_str == "" or input_date_str == None:
        input_date = current_time.strftime('%Y-%m-%d')
    else:
        input_date = input_date_str

    if input_time_str == "" or input_time_str == None:
        input_time = '00:00:00'
    else:
        input_time = input_time_str

    input_datetime_str = input_date + " " + input_time

    try:
        task_datetime = datetime.strptime(input_datetime_str, '%Y-%m-%d %H:%M')
        diff = time.mktime(task_datetime.timetuple()) - time.mktime(current_time.timetuple())

        print(f"current time={current_time}, task time={task_datetime}, date={input_date}, time={input_time}, diff={diff}")
        return True
    except Exception as e:
        print(f"invalid date time: {input_date_str}, {input_time_str}, error={str(e)}")
        return False

def get_weekday(date_str):
    # 将输入的日期字符串转换成datetime对象
    date = datetime.strptime(date_str, "%Y-%m-%d")
    
    # 获取星期几，1代表星期一，6代表星期六，0代表星期日
    weekday = date.weekday() + 1
    
    # 将数字星期转换成文字描述
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    weekday_str = weekdays[weekday-1]
    
    return weekday_str

def get_weekday_list():
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    return weekdays

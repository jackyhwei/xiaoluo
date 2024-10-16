from datetime import datetime
import time
from ...omengine.utils.datatime_utils import is_datestr_valid, OMRecurring, recurring_str_to_enum

def get_email_by_username(participants: str):
    pass

def get_phoneno_by_username(participants: str):
    pass

def get_wechat_by_username(participants: str):
    pass

def is_notify_required(start_time: str, repeat_rule: int, repeat_day: str):
    '''
    FIXME Qwen-7B-Chat llm can not parse date time value as we defined in Tool description, 
    so I decided to support loop reminder only by comparing the time field with current time
    '''
    current_time = datetime.now()
    current_date_str = current_time.strftime('%Y-%m-%d')
    current_time_str = current_time.strftime('%Y-%m-%d %H:%M')
    current_time = datetime.strptime(current_time_str, '%Y-%m-%d %H:%M')
    current_day_of_month = current_time.day
    current_month = current_time.month
    current_week_day = current_time.weekday() # 0表示星期一，6表示星期日

    # print(f"current_day={current_day}, current_weekday={current_week_day}, current time={current_time}, repeat_rule={repeat_rule}, repeat_day={repeat_day}, start_time={start_time}")

    input_date = ""
    input_time = ""

    if repeat_day == "" or repeat_day == None:
        input_date = "1"

    if start_time == "" or start_time == None:
        input_time = '00:00:00'
    else:
        input_time = start_time

    task_datetime = None
    intput_recurring_type = int(repeat_rule) 

    # print(f"OMRecurring.monthly.value={OMRecurring.monthly.value}, {3==OMRecurring.monthly.value}, {repeat_rule == OMRecurring.monthly.value}, {int(repeat_rule) == OMRecurring.monthly.value}")

    # TODO XXXXXXXXXXXXXXXXXXXXXXX
    if intput_recurring_type == OMRecurring.weekly.value:
        if current_week_day != repeat_day:
            # print(f"current week day={current_week_day}, schedule_day={repeat_day}")
            return -1
        input_datetime_str = current_date_str + " " + input_time
    elif intput_recurring_type == OMRecurring.daily.value:
        input_datetime_str = current_date_str + " " + input_time
    elif intput_recurring_type == OMRecurring.monthly.value:
        if current_day_of_month != repeat_day:
            # print(f"current day={current_day}, schedule_day={repeat_day}")
            return -1
        input_datetime_str = current_date_str + " " + input_time
    elif intput_recurring_type == OMRecurring.yearly.value:
        month_day = f"%m-%d".format(m=current_month, d=current_day_of_month)
        if month_day != repeat_day:
            return -1
        input_datetime_str = current_date_str + " " + input_time
    elif intput_recurring_type == OMRecurring.no_recurring.value:
        input_datetime_str = current_date_str + " " + input_time
    else:
        print(f"invalid recurring type: {repeat_rule}, schedule record ignored")
        return -1

    task_datetime = datetime.strptime(input_datetime_str, '%Y-%m-%d %H:%M')

    diff = time.mktime(task_datetime.timetuple()) - time.mktime(current_time.timetuple())

    # print(f"current time={current_time}, task time={task_datetime}, repeat_rule={repeat_rule}, date={input_date}, time={input_time}, diff={diff}")

    if diff <= 0:
        '''到时提醒，同时需要判断是否为一次性任务，若是，则需删除此记录'''
        return 0
    elif diff <= 60*1: 
        '''1分钟提醒'''
        return 1
    elif diff == 60*5:
        '''5分钟提醒'''
        return 5
    elif diff == 60*10:
        '''10分钟提醒'''
        return 10
    elif diff == 60*15:
        '''15分钟提醒'''
        return 15
    else:
        return -1
    
def is_notify_required2(time: str, repeat_rule: str, date: str):
    '''
    FIXME Qwen-7B-Chat llm can not parse date time value as we defined in Tool description, 
    so I decided to support loop reminder only by comparing the time field with current time
    '''
    current_time = datetime.now()
    input_date_str = ""

    print(f"current time={current_time}, repeat_rule={repeat_rule}, date={date}, time={time}")

    if date == "" or date == None:
        date = datetime.strptime(input_date_str, '%Y-%m-%d')

    if time == "" or time == None:
        time = '00:00:00'

    input_date_str = date + " " + time

    task_datetime = datetime.strptime(input_date_str, '%Y-%m-%d %H:%M:%S')

    diff = current_time - task_datetime

    print(f"current time={current_time}, task time={task_datetime}, repeat_rule={repeat_rule}, date={date}, time={time}, diff={diff}")

    if diff >= 0:
        '''到时提醒，同时需要判断是否为一次性任务，若是，则需删除此记录'''
        return 0
    elif diff == 60*1: 
        '''1分钟提醒'''
        return 1
    elif diff == 60*5:
        '''5分钟提醒'''
        return 5
    elif diff == 60*10:
        '''10分钟提醒'''
        return 10
    elif diff == 60*15:
        '''15分钟提醒'''
        return 15
    else:
        return -1
    
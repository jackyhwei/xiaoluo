import sqlite3
import threading
import datetime
import time
import logging

from omserver.omagent.omagent import OddMetaAgentCore
from omserver.model.model_schedule import SchedulesModel
from omserver.omengine.utils.datatime_utils import get_current_time

logger = logging.getLogger(__name__)

scheduled_tasks = {}
agent_running = False

# agent = OddMetaAgentCore()

# 数据库初始化
def init_db():
    # conn = sqlite3.connect('timer.db')
    # cursor = conn.cursor()
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS timer (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         time TEXT NOT NULL,
    #         repeat_rule TEXT NOT NULL,
    #         content TEXT NOT NULL,
    #         tool TEXT, 
    #         user_id INTEGER,
    #         participants TEXT,
    #         status INTEGER DEFAULT 0
    #     )
    # ''')
    # conn.commit()
    # conn.close()
    try:
        result = SchedulesModel.objects.all()
        if len(result) == 0:
            logger.debug("=> SchedulesModel is empty!")
            msg = """执行任务->
你是一个ai，你的责任是陪伴主人生活、工作，创建日程：
1、在每天早上8点提醒主人起床;
2、每天12:00及18:30提醒主人吃饭;
3、每天21:00陪主人聊聊天;
4、每天23:00提醒主人睡觉.
                """
            # fay_core.send_for_answer(msg)
            is_use_say_tool, text = agent.run(msg)

    except Exception as e:
        logger.exception("=> load SchedulesModel ERROR: %s" % str(e))

# 插入测试数据
def insert_test_data():
    # conn = sqlite3.connect('timer.db')
    # cursor = conn.cursor()
    # cursor.execute("INSERT INTO timer (time, repeat_rule, content, tool, user_id, participants, status) VALUES (?, ?, ?, ?, ?)", ('16:20', '1010001', 'Meeting Reminder', 'MeetingScheduler', 1, 'jacky, lucy', 0))
    # conn.commit()
    # conn.close()
    result = SchedulesModel.objects.all()
    if len(result) == 0:
        logger.info("=> load default SchedulesModel")
        logger.debug("------------>>>>>>>>>>>initSysDefaultSchedulesModel<<<<<<<<<<<------------")
        data = [
            {
                "time": "16:20", 
                "repeat_rule": "1010001", 
                "content": "Meeting Reminder",
                "tool": "MeetingScheduler",
                "user_id": 1,
                "participants": "jacky, lucy",
                "status": 0
            },
        ]

        logger.debug("------------>>>>>>>>>>>initSysDefaultSchedulesModel<<<<<<<<<<<------------")
        logger.debug(f"data: {data}\n")

        # 将数据转换为模型对象列表
        objects = []
        for item in data:
            obj = SchedulesModel(**item)
            objects.append(obj)
        
        # 使用bulk_create()函数进行批量创建
        SchedulesModel.objects.bulk_create(objects)

# 解析重复规则返回待执行时间，None代表不在今天的待执行计划
def parse_repeat_rule(rule, task_time):
    today = datetime.datetime.now()
    if rule == '0000000':  # 不重复
        task_datetime = datetime.datetime.combine(today.date(), task_time)
        if task_datetime > today:
            return task_datetime
        else:
            return None
    for i, day in enumerate(rule):
        if day == '1' and today.weekday() == i:
            task_datetime = datetime.datetime.combine(today.date(), task_time)
            if task_datetime > today:
                return task_datetime
    return None


# 执行任务
def execute_task(task_time, id, content):
    agent.is_chat = False
    msg = get_current_time() + " 执行任务->立刻" + content

    # fay_core.send_for_answer(msg)
    is_use_say_tool, text = agent.run(msg)
    # wsa_server.get_web_instance().add_cmd({"panelMsg": ""})

    if id in scheduled_tasks:
        del scheduled_tasks[id]

    # 如果不重复，执行后删除记录
    # conn = sqlite3.connect('timer.db')
    # cursor = conn.cursor()
    # cursor.execute("DELETE FROM timer WHERE repeat_rule = '0000000' AND time = ? AND content = ?", (task_time.strftime('%H:%M'), content))
    # conn.commit()
    # conn.close()
    result = SchedulesModel.objects.filter(repeat_rule="0000000", time=(task_time.strftime('%H:%M')), content=content)
    result.delete()

# 30秒扫描一次数据库，当扫描到今天的不存在于定时任务列表的记录，则添加到定时任务列表。执行完的记录从定时任务列表中清除。
def check_and_execute():
    while agent_running:
        # conn = sqlite3.connect('timer.db')
        # cursor = conn.cursor()
        # cursor.execute("SELECT * FROM timer where status=0")
        # rows = cursor.fetchall()

        # for row in rows:
        #     id, task_time_str, repeat_rule, content, tool, user_id, participants, status = row
        #     task_time = datetime.datetime.strptime(task_time_str, '%H:%M').time()
        #     next_execution = parse_repeat_rule(repeat_rule, task_time)

        #     if next_execution and id not in scheduled_tasks:
        #         timer_thread = threading.Timer((next_execution - datetime.datetime.now()).total_seconds(), execute_task, [next_execution, id, content])
        #         timer_thread.start()
        #         scheduled_tasks[id] = timer_thread

        # conn.close()

        rows = SchedulesModel.objects.filter(status = 0)
        for row in rows:
            print(row)

            id = row.id
            task_time_str = row.time
            repeat_rule = row.repeat_rule
            content = row.content
            tool = row.tool
            user_id = row.user_id
            participants = row.participants
            status = row.status

            task_time = datetime.datetime.strptime(task_time_str, '%H:%M').time()
            next_execution = parse_repeat_rule(repeat_rule, task_time)

            if next_execution and id not in scheduled_tasks:
                timer_thread = threading.Timer((next_execution - datetime.datetime.now()).total_seconds(), execute_task, [next_execution, id, content])
                timer_thread.start()
                scheduled_tasks[id] = timer_thread

        time.sleep(30)  # 30秒扫描一次

# agent启动
def oddmeta_agent_start():
    global agent_running
    global agent
    
    agent_running = True

    #初始计划
    # if not os.path.exists("./timer.db"):
    result = SchedulesModel.objects.all()
    if len(result) == 0:
        init_db()
    check_and_execute_thread = threading.Thread(target=check_and_execute)
    check_and_execute_thread.start()

def oddmeta_agent_stop():
    global agent_running 
    global scheduled_tasks
    # 取消所有定时任务
    for task in scheduled_tasks.values():
        task.cancel()
    agent_running = False
    scheduled_tasks = {}

if __name__ == "__main__":
    oddmeta_agent_start()

import abc
import sqlite3
from typing import Any
import ast
import logging

from langchain.tools import BaseTool

from omserver.model.model_schedule import SchedulesModel
from .OddMetaTools import OddMetaToolsBase

logger = logging.getLogger(__name__)

# class ScheduleDBQuery(BaseTool, abc.ABC):
class ScheduleDBQuery(BaseTool, OddMetaToolsBase):
    name = "ScheduleDBQuery"
    description = "用于查询、查看当前的会议、闹钟、待办、日程、提醒列表。返回的数据里包含5个参数:循环规则、日期、时间、执行的事项、用户ID、参与人"

    def __init__(self, user_id: int=0, original_input: str=None):
        super().__init__()
        OddMetaToolsBase.__init__(self, user_id, original_input)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

    def _run(self, param:str) -> str:
        logger.debug(f"=====================param={param}, userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")
        # XXX Qwen-7B-Chat llm might occationally return an invalid str like: 
        #   "('9:00', '每周星期一', '周例会', 'Jacky, Lucy, Cathy')\nObservation", 
        # we need to truncate it with \n to make it acceptable by literal_eval or eval.
        param = param[0:param.find('\n', 3)]

        result = ""

        try:
            print(f"querying database for schedules: {param}...")
            conn = sqlite3.connect('db/db.sqlite3')
            cursor = conn.cursor()
            # 执行查询
            cursor.execute("SELECT * FROM omserver_schedulesmodel where status != 1")
            # 获取所有记录
            rows = cursor.fetchall()
            # 拼接结果
            for row in rows:
                result = result +  str(row) + "\n"
            conn.commit()
            conn.close()
            print(f"querying result: {result}")
        except Exception as e:
            result = f"查询日程出错：{str(e)}"
            logger.exception(result)

        return result

if __name__ == "__main__":
    tool = ScheduleDBQuery()
    result = tool.run("")
    print(result)

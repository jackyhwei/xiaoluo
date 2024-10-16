import sqlite3
import logging
from typing import Any
from langchain.tools import BaseTool
from omserver.model.model_schedule import SchedulesModel
from asgiref.sync import sync_to_async
from .OddMetaTools import OddMetaToolsBase

logger = logging.getLogger(__name__)

class ScheduleDBDelete(BaseTool, OddMetaToolsBase):
    name = "ScheduleDBDelete"
    description = "用于删除某一个会议、闹钟、待办、日程、提醒。接受任务id作为参数，如：2"

    def __init__(self, user_id: int=0, original_input: str=None):
        super().__init__()
        OddMetaToolsBase.__init__(self, user_id, original_input)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

    def _run(self, para: str) -> str:
        from omserver.omagent import agent_service
        logger.debug(f"=====================param={para}")

        result = ""

        try:
            id = int(para)
        except ValueError:
            return "输入的 ID 无效，必须是数字。"
        
        # try:
        # except sqlite3.Error as e:
        #     return f"数据库错误: {e}"
        # 假设我们要删除主键为1的记录
        try:
            if 1:
                print(f"deleting schedule={id}")
                with sqlite3.connect('db/db.sqlite3') as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM omserver_schedulesmodel WHERE id = ?", (id,))
                    conn.commit()
                print("schedule id={id} deleted")
            else:
                obj = SchedulesModel.objects.get(id=id)
                sync_to_async(obj.delete)()

            if id in agent_service.scheduled_tasks:
                agent_service.scheduled_tasks[id].cancel()
                del agent_service.scheduled_tasks[id]

            result = f"任务 {id} 取消成功。"

        except Exception as e:
            logger.exception(result)
            result = f"删除日程计划失败：{str(e)}"

        return result

if __name__ == "__main__":
    tool = ScheduleDBDelete()
    result = tool.run("1")
    print(result)

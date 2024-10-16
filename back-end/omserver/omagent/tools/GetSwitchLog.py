import os
from typing import Any
from langchain.tools import BaseTool

import omserver.omagent.tools.IotmService as IotmService
import logging
from .OddMetaTools import OddMetaToolsBase

logger = logging.getLogger(__name__)

class GetSwitchHistory(BaseTool, OddMetaToolsBase):
    name = "GetSwitchHistory"
    description = "此工具用于查询室内的IoT设备开关当天的操作历史记录"

    def __init__(self, user_id: int=0, original_input: str=None):
        super().__init__()
        OddMetaToolsBase.__init__(self, user_id, original_input)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

    def _run(self, param: str):
        logger.debug(f"=====================param={param}, userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")

        logs = IotmService.get_switch_log()
        device_logs = {}

        switch_mapping = {
            1: '空调',
            2: '投影',
            3: '窗帘',
            4: '灯',
            5: '终端',
            6: '暖气',
            7: '投屏器'
        }

        for val in logs:
            switch_name = switch_mapping[val['number']]
            status = 'on' if val['status'] == 1 else 'off'
            info = val['timetText']

            if switch_name not in device_logs:
                device_logs[switch_name] = {'on': [], 'off': []}

            device_logs[switch_name][status].append(info)

        return device_logs

if __name__ == "__main__":
    tool = GetSwitchHistory()
    info = tool.run("")
    print(info)

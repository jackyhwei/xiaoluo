import os
from typing import Any
from itertools import groupby

from langchain.tools import BaseTool

import omserver.omagent.tools.IotmService as IotmService
import logging
from .OddMetaTools import OddMetaToolsBase

logger = logging.getLogger(__name__)

class getOnRunLinkage(BaseTool, OddMetaToolsBase):
    name = "getOnRunLinkage"
    description = "此工具用于查询会议室内的IoT设备当前在运行的联动，以及温度、湿度、烟感等的环境监控"

    def __init__(self, user_id: int=0, original_input: str=None):
        super().__init__()
        OddMetaToolsBase.__init__(self, user_id, original_input)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

    def _run(self, param: str) -> str:
        logger.debug(f"=====================param={param}, userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")

        logs = IotmService.get_on_run_linkage()
        desc_list = {
            'co2_S36': '二氧化碳',
            'light_bh1': '光照强度',
            'air_S37': '污染气体',
            'nh3_S37': '氨气',
            'temperature_MP14': '室外温度',
            'temperature_MP21': '室内温度',
            'humidity_MP14': '室外湿度',
            'humidity_S34': '室内湿度',
        }
        infos = {}

        
        logs.sort(key=lambda x: (x['label'], x['port']))

        for (sensor_type, port), group in groupby(logs, key=lambda x: (x['label'], x['port'])):
           
            group_infos = []
            for val in group:

                onoff = '开启设备开关' if val['onoff'] == 1 else '关闭设备开关'

                info = {
                    'max': val['maxVal'],
                    'min': val['minVal'],
                    'onoff': onoff,
                }
                if float(val['keeptime']) > 0:
                    info["持续时间（若需执行开启设备，持续时间过后执行关闭）,单位为分钟"] = val['keeptime']
                if float(val['delaytime']) > 0:
                    info["执行后下次检查相距时间,单位为分钟"] = val['delaytime']
                    
                group_infos.append(info)

            key_str = f"{sensor_type}_{port}"
            infos[desc_list.get(key_str, 'Unknown')] = group_infos

        return infos
if __name__ == "__main__":
    tool = getOnRunLinkage()
    info = tool.run("")
    print(info)

import os
import logging
from typing import Any

import requests
from langchain.tools import BaseTool
from urllib.parse import quote

from .OddMetaTools import OddMetaToolsBase

logger = logging.getLogger(__name__)

class Weather(BaseTool, OddMetaToolsBase):
    name = "weather"
    description = "此工具用于获取天气预报信息，需传入英文的城市名，参数格式：Guangzhou"

    def __init__(self, user_id: int=0, original_input: str=None):
        super().__init__()
        OddMetaToolsBase.__init__(self, user_id, original_input)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

    def _run(self, param: str) -> str:
        logger.debug(f"=====================param={param}, userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")

        try:
            if not param:
                return "参数不能为空"
            
            # XXX Qwen-7B-Chat llm might occationally return an invalid str like: 
            #   "('9:00', '每周星期一', '周例会', 'Jacky, Lucy, Cathy')\nObservation", 
            # we need to truncate it with \n to make it acceptable by literal_eval or eval.
            param = param[0:param.find('\n', 3)]

            encoded_city = quote(param)

            api_url = f"http://api.openweathermap.org/data/2.5/weather?q={encoded_city}&appid=272fcb70d2c4e6f5134c2dce7d091df6&lang=zh_cn"
            response = requests.get(api_url)
            if response.status_code == 200:
                weather_data = response.json()
              # 提取天气信息
                temperature_kelvin = weather_data['main']['temp']
                temperature_celsius = temperature_kelvin - 273.15
                min_temperature_kelvin = weather_data['main']['temp_min']
                max_temperature_kelvin = weather_data['main']['temp_max']
                min_temperature_celsius = min_temperature_kelvin - 273.15
                max_temperature_celsius = max_temperature_kelvin - 273.15
                description = weather_data['weather'][0]['description']
                wind_speed = weather_data['wind']['speed']

                # 构建天气描述
                weather_description = f" {description}，气温：{min_temperature_celsius:.2f}到{max_temperature_celsius:.2f}摄氏度，风速：{wind_speed} m/s。"

                return f"天气预报信息：{weather_description}"
            else:
                return f"无法获取天气预报信息，状态码：{response.status_code}"
        except Exception as e:
            return f"发生错误：{str(e)}"


if __name__ == "__main__":
    weather_tool = Weather()
    weather_info = weather_tool.run("Guangzhou")
    print(weather_info)

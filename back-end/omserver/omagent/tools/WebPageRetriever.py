from typing import Any
from langchain.tools import BaseTool
import requests
import logging

from .OddMetaTools import OddMetaToolsBase

logger = logging.getLogger(__name__)

class WebPageRetriever(BaseTool, OddMetaToolsBase):
    name = "WebPageRetriever"
    description = "专门用于通过Bing搜索API快速检索和获取与特定查询词条相关的网页信息。使用时请传入需要查询的关键词作为参数。" 

    def __init__(self, user_id: int=0, original_input: str=None):
        super().__init__()
        OddMetaToolsBase.__init__(self, user_id, original_input)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

    def _run(self, param) -> str:
        logger.debug(f"=====================param={param}, userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")

        query = param
        subscription_key = ""#请自行进行补充
        if not subscription_key:
            print("请填写bing v7的subscription_key")
            return '请填写bing v7的subscription_key'

        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}
        params = {'q': query, 'mkt': 'en-US'}  

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  
            data = response.json()  
            web_pages = data.get('webPages', {})
            return web_pages
        except Exception as e:
            print("Http Error:", e)
            return 'bing v7查询有误'


if __name__ == "__main__":
    tool = WebPageRetriever()
    result = tool.run("归纳一下近年关于“经济发展”的论文的特点和重点")
    print(result)

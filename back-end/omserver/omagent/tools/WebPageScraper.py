from bs4 import BeautifulSoup
from typing import Any
from langchain.tools import BaseTool
import requests
import logging

from .OddMetaTools import OddMetaToolsBase

logger = logging.getLogger(__name__)

class WebPageScraper(BaseTool, OddMetaToolsBase):
    name = "WebPageScraper"
    description = "此工具用于获取网页内容，使用时请传入需要查询的网页地址作为参数，如：https://www.baidu.com/。" 
 
    def __init__(self, user_id: int=0, original_input: str=None):
        super().__init__()
        OddMetaToolsBase.__init__(self, user_id, original_input)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

    def _run(self, param) -> str:
        logger.debug(f"=====================param={param}, userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        try:
            response = requests.get(param, headers=headers, timeout=10, verify=True)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except requests.exceptions.SSLCertVerificationError:
            return 'SSL证书验证失败'
        except requests.exceptions.Timeout:
            return '请求超时'
        except Exception as e:
            print("Http Error:", e)
            return '无法获取该网页内容'
        
if __name__ == "__main__":
    tool = WebPageScraper()
    result = tool.run("https://book.douban.com/review/14636204")
    print(result)
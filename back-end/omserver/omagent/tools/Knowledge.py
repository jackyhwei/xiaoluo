import os
from typing import Any
import requests
from langchain.tools import BaseTool
import logging
from .OddMetaTools import OddMetaToolsBase

logger = logging.getLogger(__name__)

class Knowledge(BaseTool, OddMetaToolsBase):
    name = "Knowledge"
    description = """此工具用于查询XX视讯视频会议系统的专业知识，使用时请传入相关问题作为参数，例如：“XXX硬终端支持H.265+RTC的会议吗”"""

    def __init__(self, user_id: int=0, original_input: str=None):
        super().__init__()
        OddMetaToolsBase.__init__(self, user_id, original_input)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

    def _run(self, param: str) -> str:
        logger.debug(f"=====================param={param}, userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")

        return "查询知识库：" + param

if __name__ == "__main__":
    tool = Knowledge()
    info = tool.run("硬终端支持与标准WebRTC SFU系统平台对接吗？")
    print(info)

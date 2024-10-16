import os
from typing import Any, Dict
import subprocess
import tempfile
import logging
from langchain.tools import BaseTool
from .OddMetaTools import OddMetaToolsBase

logger = logging.getLogger(__name__)

class PythonExecutor(BaseTool, OddMetaToolsBase):
    name = "python_executor"
    description = "此工具用于执行传入的 Python 代码片段，并返回执行结果"

    def __init__(self, user_id: int=0, original_input: str=None):
        super().__init__()
        OddMetaToolsBase.__init__(self, user_id, original_input)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

    # def _run( self, *args: Any, **kwargs: Any, ) -> Any:
    #     """Use the tool.
    #     Add run_manager: Optional[CallbackManagerForToolRun] = None
    #     to child implementations to enable tracing,
    #     """
    #     pass

    def _run(self, code: str) -> str:
        logger.debug(f"=====================param={code}, userid={OddMetaToolsBase._user_id}, original_input={OddMetaToolsBase._original_input}")
        if not code:
            return "代码不能为空"

        try:
            # 创建临时文件以写入代码
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmpfile:
                tmpfile_path = tmpfile.name
                tmpfile.write(code.encode())

            # 使用 subprocess 执行 Python 代码文件
            result = subprocess.run(['python', tmpfile_path], capture_output=True, text=True)
            # os.remove(tmpfile_path)  # 删除临时文件

            if result.returncode == 0:
                return f"执行成功：\n{result.stdout}"
            else:
                return f"执行失败，错误信息：\n{result.stderr}"

        except Exception as e:
            return f"执行代码时发生错误：{str(e)}"

if __name__ == "__main__":
    python_executor = PythonExecutor()
    code_snippet = """
print("Hello, world!")
"""
    execution_result = python_executor.run(code_snippet)
    print(execution_result)

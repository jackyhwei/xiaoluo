import json
import logging
import traceback

from ...config.sys_config import SysConfig

from typing import List
from .shorttime.memory_shorttime_impl import MemoryShortTime
from .base_storage import BaseStorage
from ..utils.snowflake_utils import SnowFlake
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

class MemoryStorageDriver():

    cfg: SysConfig
    short_memory_storage: MemoryShortTime
    long_memory_storage: any #MemoryLongTime
    snow_flake: SnowFlake = SnowFlake(data_center_id=5, worker_id=5)

    def __init__(self, memory_storage_config: dict[str, str], cfg: SysConfig) -> None:
        self.cfg = cfg
        # logger.debug("-----------------------------------------")
        self.short_memory_storage = MemoryShortTime(memory_storage_config)
        logger.debug(f"self.short_memory_storage={self.short_memory_storage}")
        if cfg.enable_longMemory:
            from .longtime.memory_longtime_impl import MemoryLongTime
            self.long_memory_storage = MemoryLongTime(memory_storage_config)
            logger.debug(f"self.long_memory_storage={self.long_memory_storage}")
        # logger.debug("-----------------------------------------")

    def search_short_memory(self, query_text: str, your_name: str, role_name: str, user_id: int) -> list[Dict[str, str]]:
        # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(f"^^^^^^^^^^^^^^^^^^^^^searching short time memories of {role_name} and user_id={user_id}")
        # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        local_memory = self.short_memory_storage.pageQuery(page_num=1, page_size=self.cfg.local_memory_num, owner=role_name, user_id=user_id)
        dict_list = []
        for json_string in local_memory:
            # FIXME jacky: 将 ' 转换为 "（因在saveMemory的时候将jsons里的 " 都替换成了 ' 。
            # print(f"json_string={json_string}")
            json_string = json_string.replace("'", "\"")
            # print(f"json_string={json_string}")
            # json内容里带换行会导致loads失败
            json_string = json_string.replace("\n", "")
            # print(f"json_string={json_string}")
            try:
                json_dict = json.loads(json_string)
                dict_list.append(json_dict)
            except Exception as e:
                logger.error(f"memory record skipped due to jons format issue: {str(e)}, str={json_string}")
        return dict_list

    def search_long_memory(self, query_text: str, your_name: str, role_name: str) -> str:
        if self.cfg.enable_longMemory:
            try:
                # 获取长期记忆，按照角色划分
                long_memory = self.long_memory_storage.search(query_text, 3, sender=your_name, owner=role_name)
                long_history = ""
                summary_historys = []
                if len(long_memory) > 0:
                    # 将json字符串转换为字典
                    for i in range(len(long_memory)):
                        summary_historys.append(long_memory[i])
                    long_history = ";".join(summary_historys)
                return long_history
            except Exception as e:
                traceback.print_exc()
                logger.error("chat error: %s" % str(e))
            return ""
        else:
            return ""

    def saveMemory(self,  your_name: str, query_text: str, role_name: str, answer_text: str, kb_id: str,
             chat_id: str,
             role_id: str,
             user_id: str,
             emotion: str,
             llm_type: str,
             user_ip: str
             ) -> None:

        # 存储短期记忆
        pk = self.get_current_entity_id()

        # print(f"input =======================> your_name={your_name}, role_name={role_name}, anser_text={answer_text}")
        # FIXME jacky: 为避免omserver.llmlocalmemorymodel表格的text字段里出现 "（双引号）从而导致对前
        #        端javascript加载内容产生影响，特将这里的"都替换为'
        #        注：search_short_memory取出时需要再将 ' 替换为 " 才能正常使用。
        local_history = {
            'ai': self.format_role_history(role_name=role_name, answer_text=answer_text),
            'human': self.format_your_history(your_name=your_name, query_text=query_text)
        }

        # print(f"save text============>answer_text={answer_text}, ========>{local_history}")

        self.short_memory_storage.saveMemory(pk, json.dumps(local_history), your_name, role_name, 1, 
                                             chat_id, 
                                             role_id, 
                                             user_id,
                                             user_ip,
                                             emotion,
                                             kb_id,
                                             llm_type,
                                             )

        # print(f"save text ok")
        # 是否开启长期记忆
        if self.cfg.enable_longMemory:
            # 将当前对话语句生成摘要
            history = self.format_history(your_name=your_name, query_text=query_text, role_name=role_name, answer_text=answer_text)
            importance_score = 3
            if self.cfg.enable_summary:
                # print("start run summary...")
                memory_summary = MemorySummary(self.cfg)
                history = memory_summary.summary(llm_model_type=self.cfg.summary_llm_model_driver_type, input=history)
                # 计算记忆的重要程度
                # print("start calculate importance...")
                memory_importance = MemoryImportance(self.cfg)
                importance_score = memory_importance.importance(self.cfg.summary_llm_model_driver_type, input=history)
            # print("start to save long memory...")
            self.long_memory_storage.saveMemory(pk, history, your_name, role_name, importance_score)

    def format_history(self, your_name: str, query_text: str, role_name: str, answer_text: str):
        your_history = self.format_your_history(your_name=your_name, query_text=query_text)
        role_history = self.format_role_history(role_name=role_name, answer_text=answer_text)
        chat_history = your_history + ';' + role_history
        return chat_history

    def format_your_history(self, your_name: str, query_text: str):
        your_history = f'{your_name}说：{query_text}'
        # your_history = query_text
        return your_history

    def format_role_history(self, role_name: str, answer_text: str):
        role_history = f'{role_name}说：{answer_text}'
        # role_history = answer_text
        return role_history

    def get_current_entity_id(self) -> int:
        '''生成唯一标识'''
        return self.snow_flake.task()

    def clear(self, owner: str) -> None:
        self.long_memory_storage.clear(owner)
        self.short_memory_storage.clear(owner)


class MemorySummary():

    cfg: SysConfig
    prompt: str

    def __init__(self, cfg: SysConfig) -> None:
        self.cfg = cfg
        self.prompt = '''
<s>[INST] <<SYS>>
Please help me extract key information about the content of the conversation, here is an example of extracting key information:
input:"alan说你好，小落，很高兴认识你，我是一名程序员，我喜欢吃东北杀猪菜;小落说我们是兼容的
output:{"summary"："alan向小落表示自己是一名程序员，alan喜欢吃杀猪菜，小落认为和alan是兼容的"}
Please export the conversation summary in Chinese.
Please use JSON format strictly and output the result:
{"Summary": "A summary of the conversation you generated"}
<</SYS>>'''

    def summary(self, llm_model_type: str, input: str) -> str:
        result = self.cfg.llm_model_driver.chat(prompt=self.prompt, type=llm_model_type, role_name="",
                                                       your_name="", query=f"input:{input}", short_history=[], long_history="")
        logger.debug("=> summary:", result)
        summary = input
        if result:
            # 寻找 JSON 子串的开始和结束位置
            start_idx = result.find('{')
            end_idx = result.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx+1]
                json_data = json.loads(json_str)
                summary = json_data["Summary"]
            else:
                logger.warn("未找到匹配的JSON字符串")
        return summary


class MemoryImportance():

    cfg: SysConfig
    prompt: str

    def __init__(self, cfg: SysConfig) -> None:
        self.cfg = cfg
        self.prompt = '''
<s>[INST] <<SYS>>
There is a scoring mechanism for the importance of memory, on a scale of 10, where 1 is a mundane task (eg, brushing your teeth, making your bed) and 10 is an impressive extremely and important task (eg, breaking up, college admissions), Please help me evaluate the importance score of the following memory.
Please do not output the inference process, just output the scoring results.
Please output the results strictly in JSON format:
{"score": "The rating result you generated"}
<</SYS>>'''

    def importance(self, llm_model_type: str, input: str) -> int:
        result = self.cfg.llm_model_driver.chat(prompt=self.prompt, type=llm_model_type, role_name="",
                                                       your_name="", query=f"memory:{input}", short_history=[], long_history="")
        logger.debug("=> score:", result)
        # 寻找 JSON 子串的开始和结束位置
        start_idx = result.find('{')
        end_idx = result.rfind('}')
        score = 3
        if start_idx != -1 and end_idx != -1:
            json_str = result[start_idx:end_idx+1]
            json_data = json.loads(json_str)
            score = int(json_data["score"])
        else:
            logger.warn("未找到匹配的JSON字符串")
        return score

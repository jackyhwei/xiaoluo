import datetime
import logging
import json
import traceback
import jieba
import jieba.analyse
from django.db.models import Q
from ..base_storage import BaseStorage
from omserver.model.model_llm import LlmLocalMemoryModel

# TODO 搜索方式待整改
logger = logging.getLogger(__name__)

class MemoryShortTime(BaseStorage):

    def __init__(self, memory_storage_config: dict[str, str]):
        logger.info("=> Load MemoryShortTime Success")

    def search(self, query_text: str, limit: int, owner: str) -> list[str]:
        # 使用 Q 对象组合查询条件，
        query = Q(owner=owner)

        # 查询结果，并限制数量
        results = LlmLocalMemoryModel.objects.filter(query).order_by('-timestamp')[:limit]

        # 提取查询结果的 text 字段
        result_texts = [result.text for result in results]
        return result_texts

    def pageQuery(self, page_num: int, page_size: int, owner: str, user_id: int) -> list[str]:
        # 计算分页偏移量
        offset = (page_num - 1) * page_size

        # 分页查询，并提取 text 字段
        results = LlmLocalMemoryModel.objects.filter(owner=owner, user_id=user_id).order_by('-timestamp').values_list('text', flat=True)[offset:offset + page_size]
        return list(results)

    def saveMemory(self, pk: int,  query_text: str, sender: str, owner: str, importance_score: int, 
                   chat_id: str, role_id: int, user_id: int, user_ip: str, 
                   emotion: str, kb_id: str, llm_type: str) -> None:
        # FIXME jacky：将" 替换成 '，以避免到前端后javascript解析json报错
        # 历史记录暂用以下命令来替换数据库：update omserver_llmlocalmemorymodel set text=replace(text, '"', '''') where text like '%"%'
        logger.debug(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^local_history={query_text}")

        try:
            text = query_text.encode().decode('unicode_escape')

            logger.debug(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^text={text}")

            query_words = jieba.cut(text, cut_all=False)
            query_tags = list(query_words)
            keywords = jieba.analyse.extract_tags(" ".join(query_tags), topK=20)

            logger.debug(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^keywords={keywords}")

            text = text.replace("\"", "\'")

            current_timestamp = datetime.datetime.now().isoformat()  #
            local_memory_model = LlmLocalMemoryModel(
                id=pk,
                text=text,
                tags=",".join(keywords),  # 设置标签
                sender=sender,
                owner=owner,
                timestamp=current_timestamp,
                chat_id=chat_id,
                role_id=role_id,
                user_id=user_id,
                user_ip=user_ip,
                emotion=emotion,
                kb_id=kb_id,
                llm_type=llm_type
            )
            local_memory_model.save()
            logger.debug(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^saved ok")
        except Exception as e:
            logger.exception("=> saveMemory failed: %s" % str(e))
            traceback.print_exc()

    def clear(self, owner: str) -> None:
        # 清除指定 owner 的记录
        LlmLocalMemoryModel.objects.filter(owner=owner).delete()

import os
import math
import logging

from langchain.memory import VectorStoreRetrieverMemory
import faiss

from langchain.agents import Tool, initialize_agent, agent_types, create_react_agent
from langchain import hub
# from langchain_community.llms import OpenAI
# from langchain.agents import AgentExecutor, create_react_agent

from .tools.ScheduleAdder import ScheduleAdder
from .tools.Weather import Weather
from .tools.CheckSensor import GetSensorStatus
from .tools.Switch import ApplianceSwitch
from .tools.Knowledge import Knowledge
#from .tools.Say import Say
from .tools.ScheduleDBQuery import ScheduleDBQuery
from .tools.ScheduleDBDelete import ScheduleDBDelete
from .tools.GetSwitchLog import GetSwitchHistory
from .tools.getOnRunLinkage import getOnRunLinkage
from .tools.PythonExecutor import PythonExecutor
from .tools.WebPageRetriever import WebPageRetriever
from .tools.WebPageScraper import WebPageScraper
from .tools.KnowledgeBaseResponder import KnowledgeBaseResponder

# from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings

# from langchain.chat_models import ChatOpenAI
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI

# from langchain.docstore import InMemoryDocstore
from langchain_community.docstore import InMemoryDocstore
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
# from langchain.callbacks import get_openai_callback
from langchain_community.callbacks.manager import get_openai_callback

from langchain.retrievers import TimeWeightedVectorStoreRetriever

from omserver.mainservice.messages.chat_live_message import ChatLiveMessage, put_message
from omserver.omengine.utils.datatime_utils import get_current_time

logger = logging.getLogger(__name__)


# def do_agent_action(msg: str):
#     manager = RandomEmotion()
#     random_action = manager.random_action()
#     logger.info(f"Do Agent Action: {msg}, Emote:{random_action.random_emote}")
#     put_message(ChatMessage(type="agent_action", user_name="agent", content=msg, emote=random_action.random_emote))


class OddMetaAgentCore():
    def __init__(self):
        LLM_API_KEY = os.environ.get('LLM_API_KEY', "")
        LLM_BASE_URL = os.environ.get('LLM_BASE_URL', "")
        LLM_MODEL = os.environ.get('LLM_MODEL', "")

        # #使用open ai embedding
        # embedding_size = 1536  # OpenAIEmbeddings 的维度
        # index = faiss.IndexFlatL2(embedding_size)
        # embedding_fn = OpenAIEmbeddings()

        #创建llm
        self.llm = ChatOpenAI(model_name=LLM_MODEL, openai_api_key=LLM_API_KEY, openai_api_base=LLM_BASE_URL, temperature=0.7, verbose=True)

        # #创建向量数据库
        # def relevance_score_fn(score: float) -> float:
        #     return 1.0 - score / math.sqrt(2)
        # vectorstore = FAISS(embedding_fn, index, InMemoryDocstore({}), {}, relevance_score_fn=relevance_score_fn)

        # # 创建记忆(斯坦福小镇同款记忆检索机制:时间、相关性、重要性三个维度)
        # retriever = TimeWeightedVectorStoreRetriever(vectorstore=vectorstore, other_score_keys=["importance"], k=3)  
        # self.agent_memory = VectorStoreRetrieverMemory(memory_key="history", retriever=retriever)

        # 保存基本信息到记忆
        # utils.load_config()
        # attr_info = ", ".join(f"{key}: {value}" for key, value in utils.config["attribute"].items())
        # self.agent_memory.save_context({"input": "我的基本信息是?"}, {"output": attr_info})

        #内存保存聊天历史
        self.chat_history = []

        #创建agent chain
        schedule_adder_tool = ScheduleAdder()
        query_schedules_tool = ScheduleDBQuery()
        schedule_delete_tools = ScheduleDBDelete()
        weather_tool = Weather()
        python_executor = PythonExecutor()
        switch_tool = ApplianceSwitch()
        knowledge_tool = Knowledge()
        query_sensor_status = GetSensorStatus()
        query_switch_history = GetSwitchHistory()
        query_on_run_linkage = getOnRunLinkage()
        web_page_retriever = WebPageRetriever()
        web_page_scraper = WebPageScraper()
        knowledge_base_responder = KnowledgeBaseResponder()
        
        self.tools = [
            Tool(
                name=python_executor.name,
                func=python_executor.run,
                description=python_executor.description
            ),
            Tool(
                name=schedule_adder_tool.name,
                func=schedule_adder_tool.run,
                description=schedule_adder_tool.description
            ),
            Tool(
                name=weather_tool.name,
                func=weather_tool.run,
                description=weather_tool.description
            ),
            Tool(
                name=query_sensor_status.name,
                func=query_sensor_status.run,
                description=query_sensor_status.description
            ),
            Tool(
                name=switch_tool.name,
                func=switch_tool.run,
                description=switch_tool.description
            ),
            Tool(
                name=knowledge_tool.name,
                func=knowledge_tool.run,
                description=knowledge_tool.description
            ),
            Tool(
                name=query_schedules_tool.name,
                func=query_schedules_tool.run,
                description=query_schedules_tool.description
            ),
            Tool(
                name=schedule_delete_tools.name,
                func=schedule_delete_tools.run,
                description=schedule_delete_tools.description
            ),
            Tool(
                name=query_switch_history.name,
                func=query_switch_history.run,
                description=query_switch_history.description
            ),
            Tool(
                name=query_on_run_linkage.name,
                func=query_on_run_linkage.run,
                description=query_on_run_linkage.description
            ),
            Tool(
                name=web_page_retriever.name,
                func=web_page_retriever.run,
                description=web_page_retriever.description
            ),
            Tool(
                name=web_page_scraper.name,
                func=web_page_scraper.run,
                description=web_page_scraper.description
            ),
            Tool(
                name=knowledge_base_responder.name,
                func=knowledge_base_responder.run,
                description=knowledge_base_responder.description
            )
        ]

        self.agent = initialize_agent(agent_types=agent_types.AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                        tools=self.tools, llm=self.llm, verbose=True,
                        max_history=5, handle_parsing_errors=True)

        # self.prompt = hub.pull("hwchase17/react")
        # self.agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=self.prompt)

        #记录一轮执行有无调用过say tool
        self.is_use_say_tool = False
        self.say_tool_text = ""

        self.total_tokens = 0
        self.total_cost = 0

    #记忆prompt
    def format_history_str(self, str):
        result = ""
        history_string = str['history']

        # Split the string into lines
        lines = history_string.split('input:')

        # Initialize an empty list to store the formatted history
        formatted_history = []

        #处理记忆流格式
        for line in lines:
            if "output" in line:
                input_line = line.split("output:")[0].strip()
                output_line = line.split("output:")[1].strip()
                formatted_history.append({"input": input_line, "output": output_line})
        
        # 记忆流转换成字符串
        result += "-以下是与用户说话关连度最高的记忆：\n"
        for i in range(len(formatted_history)):
            if i >= 3:
                break
            line = formatted_history[i]
            result += f"--input：{line['input']}\n--output：{line['output']}\n"
        if len(formatted_history) == 0:
            result += "--没有记录\n"

        #添加内存记忆
        formatted_history = []
        for line in self.chat_history:
            formatted_history.append({"input": line[0], "output": line[1]})
        
        #格式化内存记忆字符串
        result += "\n-以下刚刚的对话：\n"
        for i in range(len(formatted_history)):
            line = formatted_history[i]
            result += f"--input：{line['input']}\n--output：{line['output']}\n"
        if len(formatted_history) == 0:
            result += "--没有记录\n"

        return result
    
    def run(self, input_text):
        self.is_use_say_tool = False
        self.say_tool_text = ""
        
        result = ""
        history = ""
        # history = self.agent_memory.load_memory_variables({"input":input_text.replace('主人语音说了：', '').replace('主人文字说了：', '')})
        # history = self.format_history_str(history)
        try:
            input_text = input_text.replace('主人语音说了：', '').replace('主人文字说了：', '')
            agent_prompt = """
现在时间是：{now_time}。你是一个罗索工作室的AI助手，负责协助主人打理主人的生活、工作。请依据以下信息为主人服务 ：
{history}
input：{input_text}
output：
""".format(history=history, input_text=input_text, now_time=get_current_time())
            with get_openai_callback() as cb:
                result = self.agent.run(agent_prompt)
                self.total_tokens = self.total_tokens + cb.total_tokens
                self.total_cost = self.total_cost + cb.total_cost
                logger.debug("本次消耗token:{}， Cost (USD):{}，共消耗token:{}， Cost (USD):{}".format(cb.total_tokens, cb.total_cost, self.total_tokens, self.total_cost))

        except Exception as e:
            print(e)

        result = "执行完毕" if result is None or result == "N/A" else result
        chat_text = self.say_tool_text if self.is_use_say_tool else result

        #保存到记忆流和聊天对话
        # self.agent_memory.save_context({"input": input_text.replace('主人语音说了：', '').replace('主人文字说了：', '')},{"output": result})
        self.chat_history.append((input_text.replace('主人语音说了：', '').replace('主人文字说了：', ''), chat_text))
        if len(self.chat_history) > 5:
            self.chat_history.pop(0)

        put_message(ChatLiveMessage(type="user", user_name="sys", query=input_text, 
                                    role_name="agent", content=chat_text, emote="neutral"))

        return self.is_use_say_tool, chat_text

if __name__ == "__main__":
    agent = OddMetaAgentCore()
    print(agent.run("你好"))


# from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain

from pydantic import BaseModel, Field
from typing import Any, List
from langchain.schema import HumanMessage
# from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory
import faiss
# from langchain.docstore import InMemoryDocstore
from langchain_community.docstore import InMemoryDocstore
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS

#from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
#from langchain_community.chat_models import ChatOpenAI

# from langchain.callbacks import get_openai_callback
from langchain_community.callbacks.manager import get_openai_callback

# from langchain_community.output_parsers.rail_parser import GuardrailsOutputParser

from langchain.agents import Agent, Tool, initialize_agent, agent_types,create_react_agent, AgentExecutor
from langchain import hub
# from langsmith import Client
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder

from langchain.tools import BaseTool

from tools.ScheduleAdder import ScheduleAdder
from tools.Weather import Weather
from tools.PythonExecutor import PythonExecutor
from omserver.omengine.utils.datatime_utils import get_current_time

import logging
import abc


logger = logging.getLogger(__name__)

# 创建一个自定义Agent，其中可以捕获原始输入
class OddMetaTool(BaseTool):
    def __init__(self):
        super().__init__()

class QueryLoopType(OddMetaTool, abc.ABC):
    name = "QueryLoopType"
    description = "用于查询指定任务是否有循环，请选择以下几种输出格式进行输出：每天、每周的某一天、每月的某一天、每年的某一天、不循环。示例输出格式：每天、每周一、每月10号、每年11月25日、不循环"

    def __init__(self):
        super().__init__()

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass

    def _run(self, para: str) -> Any:
        logger.debug(f"=====================param={para}")

        run_counter = 0
        user_input = para
        response = ""
        
        return response

# 创建一个自定义Agent，其中可以捕获原始输入
class CustomAgent(Agent):
    original_input: str

    def __init__(self, tools, **kwargs):
        super().__init__(tools, **kwargs)
        self.original_input = None

    def _predict(self, inputs, **kwargs):
        # 在这里捕获原始输入
        self.original_input = inputs[0]
        return super()._predict(inputs, **kwargs)
    
class OmAgentCore():
    _tools: any
    _llm: ChatOpenAI
    _agent: any
    is_use_say_tool: bool
    say_tool_text: str
    total_tokens: int
    total_cost: int

    _langchain_ver: int

    _session_state: Any

    def __init__(self):
        python_executor = PythonExecutor()
        schedule_adder = ScheduleAdder()
        weather_tool = Weather()

        self.total_cost = 0
        self.total_tokens = 0
        self.say_tool_text = ""
        self.is_use_say_tool = False

        self._langchain_ver = 1

        # 初始会话状态，可以包含原始输入
        self._session_state = {"original_input": None}

        #创建llm
        # self.llm = ChatOpenAI(model="gpt-4-0125-preview", verbose=True)
        self._llm = ChatOpenAI(
            openai_api_key='sk-cCwAxfqbrU2DlKVIA6B36b75B4924eE09e9eCbD378B7B3Be',
            base_url='https://rg4.net/v1',
            model='Qwen-7B-Chat',
            temperature=0,
            )

        self._tools = [
            Tool(
                name=python_executor.name,
                func=python_executor.run,
                description=python_executor.description
            ),
            Tool(
                name=schedule_adder.name,
                func=schedule_adder.run,
                description=schedule_adder.description
            ),
            Tool(
                name=weather_tool.name,
                func=weather_tool.run,
                description=weather_tool.description
            ),
        ]

        if self._langchain_ver == 0:
            self._agent = initialize_agent(agent_types=agent_types.AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                            tools=self._tools, llm=self._llm, verbose=True,
                            max_history=5, handle_parsing_errors=True)
        else:
            # self._prompt = hub.pull("hwchase17/react")

            template = '''Answer the following questions as best you can. You have access to the following tools:

            {tools}

            Use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of [{tool_names}]
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question

            Begin!

            Question: {input}
            Thought:{agent_scratchpad}'''

            self._prompt = PromptTemplate.from_template(template)

            print(self._prompt)

            self._agent = create_react_agent(llm=self._llm, tools=self._tools, prompt=self._prompt)
            # executes the logical steps we created
            self._agent_executor = AgentExecutor(
                agent=self._agent, 
                tools=self._tools,
                verbose=True,
                handle_parsing_errors=True,
                return_intermediate_steps = True,
                max_iterations = 5 # useful when agent is stuck in a loop
                )


    def run(self, input_text):
        self.is_use_say_tool = False
        self.say_tool_text = ""

        result = ""
        history = ""
        # history = self.agent_memory.load_memory_variables({"input":input_text.replace('主人语音说了：', '').replace('主人文字说了：', '')})
        # history = self.format_history_str(history)

        self._session_state["original_input"] = input_text

        try:
            with get_openai_callback() as cb:
                if self._langchain_ver == 0:
                    input_text = input_text.replace('主人语音说了：', '').replace('主人文字说了：', '')
                    agent_prompt = "现在时间是：{now_time}。你是一个罗索实验室的AI，负责协助主人打理生活、工作。请依据以下信息为主人服务 ： \
{history} \
input：{input_text} \
output： \
""".format(history=history, input_text=input_text, now_time=get_current_time())
                    result = self._agent.run(agent_prompt, session_state=self._session_state)
                else:
                    # rsp = self._agent_executor.invoke({"input": input_text, "session_state": self._session_state})
                    rsp = self._agent_executor.invoke(input_text, session_state=self._session_state)
                    print(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^rsp={rsp}")
                    result = rsp["output"]
                    print(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^result={result}")

                self.total_tokens = self.total_tokens + cb.total_tokens
                self.total_cost = self.total_cost + cb.total_cost
                logger.debug("本次消耗token:{}， Cost (USD):{}，共消耗token:{}， Cost (USD):{}".format(cb.total_tokens, cb.total_cost, self.total_tokens, self.total_cost))

        except Exception as e:
            print(e)
        
        result = "执行完毕" if result is None or result == "N/A" else result
        chat_text = self.say_tool_text if self.is_use_say_tool else result

        # # 保存到记忆流和聊天对话
        # self.agent_memory.save_context({"input": input_text.replace('主人语音说了：', '').replace('主人文字说了：', '')},{"output": result})
        # self.chat_history.append((input_text.replace('主人语音说了：', '').replace('主人文字说了：', ''), chat_text))
        # if len(self.chat_history) > 5:
        #     self.chat_history.pop(0)

        return self.is_use_say_tool, chat_text


if __name__ == "__main__":

    agent = OmAgentCore()

    text = "为一家生产彩色袜子的公司起一个好名字是什么？"
    text = "帮我定个明天上午7点半的闹钟, 提醒我起床"
    text = "查看日程安排"
    text = "明天上海的天气怎么样？"

    # messages = [HumanMessage(content=text)]
    result = agent.run(text)
    print(result)

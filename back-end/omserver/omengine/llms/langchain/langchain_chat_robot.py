import logging
import os

from dotenv import find_dotenv
import openai
import traceback

from langchain.schema import ( HumanMessage, )

from langchain.agents import Tool, initialize_agent, agent_types, create_react_agent, AgentExecutor, create_structured_chat_agent
from langchain import hub
# from langchain_community.llms import OpenAI
# from langchain.agents import AgentExecutor, create_react_agent

# from langchain.docstore import InMemoryDocstore
from langchain_community.docstore import InMemoryDocstore
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS

#from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
#from langchain_community.chat_models import ChatOpenAI

# from langchain.callbacks import get_openai_callback
from langchain_community.callbacks.manager import get_openai_callback

# from langsmith import Client
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder, SystemMessagePromptTemplate

from ...utils.str_utils import filter_spaces_and_tabs, filter_tabs
from ...utils.datatime_utils import get_current_time

from omserver.omagent.tools.ScheduleAdder import ScheduleAdder
from omserver.omagent.tools.Weather import Weather
from omserver.omagent.tools.ScheduleDBQuery import ScheduleDBQuery
from omserver.omagent.tools.ScheduleDBDelete import ScheduleDBDelete
from omserver.omagent.tools.PythonExecutor import PythonExecutor
from omserver.omagent.tools.MeetingScheduler import MeetingScheduler, MeetingSchedulerInput
# from omserver.omagent.tools.CheckSensor import GetSensorStatus
# from omserver.omagent.tools.Switch import ApplianceSwitch
# from omserver.omagent.tools.Knowledge import Knowledge
# from omserver.omagent.tools.GetSwitchLog import GetSwitchHistory
# from omserver.omagent.tools.getOnRunLinkage import getOnRunLinkage
# from omserver.omagent.tools.WebPageRetriever import WebPageRetriever
# from omserver.omagent.tools.WebPageScraper import WebPageScraper
# from omserver.omagent.tools.KnowledgeBaseResponder import KnowledgeBaseResponder
# from omserver.omagent.tools.QueryDate import QueryDate

from langchain.schema.output_parser import BaseLLMOutputParser

logger = logging.getLogger(__name__)

class MyOutputParser(BaseLLMOutputParser):
    def __init__(self):
        super().__init__()

    def parse_result(self, output):
        # cut_off = output.find("\n", 3)
        # # delete everything after new line
        # return output[:cut_off]
        print(f"$$$$$$$$$$$$$$$$$$$$$$$$$$：{output}")
        return output

class LangchainGeneration():

    _llm: ChatOpenAI

    _tools: any
    _agent: any
    _prompt: any
    # _client: Client
    _agent_mode: int
    _agent_executor: AgentExecutor

    is_use_say_tool: bool
    say_tool_text: str
    total_tokens: int
    total_cost: int

    def init_agent(self, query: str, user_id: int):
        from dotenv import load_dotenv
        load_dotenv()

        LLM_API_KEY = os.environ.get('LLM_API_KEY', "")
        LLM_BASE_URL = os.environ.get('LLM_BASE_URL', "")
        LLM_MODEL = os.environ.get('LLM_MODEL', "")

        if LLM_MODEL == None or LLM_MODEL == "":
            LLM_MODEL = "gpt-3.5-turbo"

        print("=================================================")
        print("=================================================")
        print(f"LangchainGeneration, model={LLM_MODEL}")
        print("=================================================")
        print("=================================================")

        #创建llm
        if LLM_BASE_URL != None and LLM_BASE_URL != "":
            self._llm = ChatOpenAI(temperature=0.7, model_name=LLM_MODEL, openai_api_key=LLM_API_KEY, openai_api_base=LLM_BASE_URL, streaming=True)
        else:
            self._llm = ChatOpenAI(temperature=0.7, model_name=LLM_MODEL, openai_api_key=LLM_API_KEY)

        self.total_cost = 0
        self.total_tokens = 0
        self.say_tool_text = ""
        self.is_use_say_tool = False

        self._agent_mode = 0        # initialize_agent
        self._agent_mode = 2        # create_structured_chat_agent
        self._agent_mode = 1        # create_react_agent

        print("--------------------------------------")
        print(f"user_id={user_id}, query={query}")
        print("--------------------------------------")

        #创建agent chain
        weather_tool = Weather(user_id=user_id, original_input=query)
        schedule_query_tool = ScheduleDBQuery(user_id=user_id, original_input=query)
        schedule_delete_tool = ScheduleDBDelete(user_id=user_id, original_input=query)
        python_executor = PythonExecutor(user_id=user_id, original_input=query)
        meeting_scheduler = MeetingScheduler(user_id=user_id, original_input=query)
        # schedule_adder_tool = ScheduleAdder(user_id=user_id, original_input=query)
        # check_sensor_tool = GetSensorStatus(user_id=user_id, original_input=query)
        # switch_tool = ApplianceSwitch(user_id=user_id, original_input=query)
        # knowledge_tool = Knowledge(user_id=user_id, original_input=query)
        # # say_tool = Say()
        # get_switch_log = GetSwitchHistory(user_id=user_id, original_input=query)
        # get_on_run_linkage = getOnRunLinkage(user_id=user_id, original_input=query)
        # web_page_retriever = WebPageRetriever(user_id=user_id, original_input=query)
        # web_page_scraper = WebPageScraper(user_id=user_id, original_input=query)
        # knowledge_base_responder = KnowledgeBaseResponder(user_id=user_id, original_input=query)
        # query_date = QueryDate()
        
        self._tools = [
            Tool(
                name=weather_tool.name,
                func=weather_tool.run,
                description=weather_tool.description
            ),
            Tool(
                name=python_executor.name,
                func=python_executor.run,
                description=python_executor.description
            ),
            # Tool(
            #     name=schedule_adder_tool.name,
            #     func=schedule_adder_tool.run,
            #     description=schedule_adder_tool.description
            # ),
            Tool(
                name=schedule_query_tool.name,
                func=schedule_query_tool.run,
                description=schedule_query_tool.description
            ),
            Tool(
                name=schedule_delete_tool.name,
                func=schedule_delete_tool.run,
                description=schedule_delete_tool.description
            ),
            Tool(
                name=meeting_scheduler.name,
                func=meeting_scheduler.run,
                description=meeting_scheduler.description,
                # args_schema = MeetingSchedulerInput,
                # coroutine=
                # return_direct = True
            ),
            # Tool(
            #     name=query_date.name,
            #     func=query_date.run,
            #     description=query_date.description
            # ),
            # Tool(
            #     name=check_sensor_tool.name,
            #     func=check_sensor_tool.run,
            #     description=check_sensor_tool.description
            # ),
            # Tool(
            #     name=switch_tool.name,
            #     func=switch_tool.run,
            #     description=switch_tool.description
            # ),
            # Tool(
            #     name=knowledge_tool.name,
            #     func=knowledge_tool.run,
            #     description=knowledge_tool.description
            # ),
            # Tool(
            #     name=say_tool.name,
            #     func=say_tool.run,
            #     description=say_tool.description
            # ),
            # Tool(
            #     name=get_switch_log.name,
            #     func=get_switch_log.run,
            #     description=get_switch_log.description
            # ),
            # Tool(
            #     name=get_on_run_linkage.name,
            #     func=get_on_run_linkage.run,
            #     description=get_on_run_linkage.description
            # ),
            # Tool(
            #     name=web_page_retriever.name,
            #     func=web_page_retriever.run,
            #     description=web_page_retriever.description
            # ),
            # Tool(
            #     name=web_page_scraper.name,
            #     func=web_page_scraper.run,
            #     description=web_page_scraper.description
            # ),
            # Tool(
            #     name=knowledge_base_responder.name,
            #     func=knowledge_base_responder.run,
            #     description=knowledge_base_responder.description
            # ),
        ]

        try:
            if self._agent_mode == 0:
                my_agent_type = agent_types.AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION
                my_agent_type = agent_types.AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION

                self._agent = initialize_agent(
                    agent_types=my_agent_type,
                    tools=self._tools, llm=self._llm, verbose=True,
                    output_parser= MyOutputParser,
                    max_history=5, handle_parsing_errors=True)
            elif self._agent_mode == 1:
                # when self._agent_mode == 1:
                if os.environ.get('enable_smith', "False") == "True":
                    self._prompt = hub.pull("hwchase17/react")
                else:
                    self._prompt = (SystemMessagePromptTemplate.from_template("You are a nice assistant.")
                        + "Answer the following questions as best you can. You have access to the following tools:\
\
{tools} \
\
Use the following format: \
Question: the input question you must answer \
Thought: you should always think about what to do \
Action: the action to take, should be one of [{tool_names}] \
Action Input: the input to the action \
Observation: the result of the action \
... (this Thought/Action/Action Input/Observation can repeat N times) \
Thought: I now know the final answer \
Final Answer: the final answer to the original input question \
\
Begin! \
\
Question: {input} \
Thought:{agent_scratchpad}"
                        )

                print(self._prompt)

                self._agent = create_react_agent(llm=self._llm, tools=self._tools, prompt=self._prompt)
                # self._agent = create_structured_chat_agent(llm=self._llm, tools=self._tools, prompt=self._prompt)

                # executes the logical steps we created
                self._agent_executor = AgentExecutor(
                    agent=self._agent, 
                    tools=self._tools,
                    verbose=True,
                    handle_parsing_errors=True,
                    # return_intermediate_steps = True,
                    output_parser = MyOutputParser,
                    max_iterations = 5 # useful when agent is stuck in a loop
                    )
            else:
                # when self._agent_mode == 1:
                if os.environ.get('enable_smith', "False") == "True":
                    self._prompt = hub.pull("hwchase17/react")
                else:
                    self._prompt = (SystemMessagePromptTemplate.from_template("You are a nice assistant.")
                        + "Answer the following questions as best you can. You have access to the following tools:\
\
{tools} \
\
Use the following format: \
Question: the input question you must answer \
Thought: you should always think about what to do \
Action: the action to take, should be one of [{tool_names}] \
Action Input: the input to the action \
Observation: the result of the action \
... (this Thought/Action/Action Input/Observation can repeat N times) \
Thought: I now know the final answer \
Final Answer: the final answer to the original input question \
\
Begin! \
\
Question: {input} \
Thought:{agent_scratchpad}"
                        )

                print(self._prompt)

                self._agent = create_structured_chat_agent(llm=self._llm, tools=self._tools, prompt=self._prompt)

                # executes the logical steps we created
                self._agent_executor = AgentExecutor(
                    agent=self._agent, 
                    tools=self._tools,
                    verbose=True,
                    handle_parsing_errors=True,
                    return_intermediate_steps = True,
                    output_parser = MyOutputParser,
                    max_iterations = 5 # useful when agent is stuck in a loop
                    )

        except Exception as e:
            traceback.print_exc()
            logger.error("===============================================chat error: %s" % str(e))

    def __init__(self, query: str, user_id: int )-> None:

        self.init_agent(query=query, user_id=user_id)
        pass

    def chat(self, prompt: str, role_name: str, your_name: str, query: str, kb_id: str, short_history: list[dict[str, str]], long_history: str) -> str:
        # FIXME jacky, maybe we shouldn't add query to prompt, disable it temparary
        # prompt = prompt + query
        # logger.debug(f"prompt:{prompt}")
        llm_result = self._llm.generate(
            messages=[[HumanMessage(content=prompt)]])
        llm_result_text = llm_result.generations[0][0].text
        return llm_result_text


    async def chatStream(self,
                         prompt: str,
                         role_name: str,
                         your_name: str,
                         query: str,
                         kb_id: str,
                         history: list[dict[str, str]],
                         realtime_callback=None,
                         conversation_end_callback=None,
                         chat_id:str=None,
                         role_id:int=0,
                         user_id:int=0,
                         emotion:str=None,
                         llm_type:str=None,
                         user_ip:str=None
                         ):
        
        # logger.debug(f"prompt:{prompt}")
        messages = []
        # for item in history:
        #     message = {"role": "user", "content": item["human"]}
        #     messages.append(message)
        #     message = {"role": "assistant", "content": item["ai"]}
        #     messages.append(message)
        messages.append({'role': 'system', 'content': prompt})
        messages.append({'role': 'user', 'content': your_name + "说：" + query})
        # messages.append({'role': 'user', 'content': query})

        logger.debug(f"------------------------------kb_id={kb_id}, your_name={your_name}, role_name={role_name}, message={messages}")

        result = ""
        answer = ""
        agent_prompt =""

        # TODO Knowledge Base mode to be implemented
        try:
            # FIXME 加入了小落内置的prompt后反而导致了tools识别准确率下降，暂禁用内置prompt。
#             agent_prompt = """
# 现在时间是：{now_time}。{prompt} ：
# {history}
# input：{input_text}
# output：
# """.format(history=history, input_text=query, now_time=get_current_time(), prompt=prompt)
            # FIXME 加入了历史聊天记录，导致langchain agent tool不工作，暂禁用
#             agent_prompt = """
# 现在时间是：{now_time}。
# {your_name}说：{input_text}。
# 你的{your_name}的历史对话记录：{history}。
# output：
# """.format(history=history, input_text=query, your_name=your_name, now_time=get_current_time())

            
            if self._agent_mode == 0:
                agent_prompt = """
现在时间是：{now_time}。
{your_name}说：{input_text}。
output：
""".format(input_text=query, your_name=your_name, now_time=get_current_time())
            else:
                agent_prompt = ""

            with get_openai_callback() as cb:
                if self._agent_mode == 0:
                    result = self._agent.run({"input", agent_prompt})
                else:
                    # when self._agent_mode == 1:
                    '''
Answer the following questions as best you can. You have access to the following tools:

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
Thought:{agent_scratchpad}
                    '''
                    rsp = self._agent_executor.invoke({"input": query})
                    print(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^rsp={rsp}")
                    result = rsp["output"]
                    print(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^result={result}")

                self.total_tokens = self.total_tokens + cb.total_tokens
                self.total_cost = self.total_cost + cb.total_cost

                # FIXME jacky：中文的时候需要过滤空格，但是英文又不能过滤空格，头疼
                # content = filter_spaces_and_tabs(result)
                content = filter_tabs(result)

                answer += content
                logger.debug(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^chatStream:realtime_callback, answer={answer}")
                if realtime_callback:
                    realtime_callback(role_name, your_name, query, content, kb_id, False, chat_id, role_id, user_id, emotion, llm_type, user_ip)  # 调用实时消息推送的回调函数

                logger.debug("本次消耗token:{}， Cost (USD):{}，共消耗token:{}， Cost (USD):{}".format(cb.total_tokens, cb.total_cost, self.total_tokens, self.total_cost))

        except Exception as e:
            print(e)
        
        result = "执行完毕" if result is None or result == "N/A" else result
        answer = self.say_tool_text if self.is_use_say_tool else result

        '''回答结束
        '''
        logger.debug(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^chatStream:conversation_end_callback, answer={answer}")
        if conversation_end_callback:
            conversation_end_callback(role_name, answer, your_name, query, kb_id, chat_id, role_id, user_id, emotion, llm_type, user_ip)  # 调用对话结束消息的回调函数

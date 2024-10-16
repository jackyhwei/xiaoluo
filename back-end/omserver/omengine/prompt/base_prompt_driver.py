from abc import ABC, abstractmethod
from ..character.character import Character

class BaseCharacterPrompt(ABC):

    '''统一自定义角色模版抽象类,基于当前抽象类扩展其他的自定义角色模版'''
    ## 支持的外部参数
    # your_name = "{your_name}"
    # long_history = "{long_history}"
    # input_prompt = "{input_prompt}"
    # input = "{input}"
    # current_time = "{current_time}"

    PROMPT: str
    PERSONALITY_PROMPT: str
    SCENARIO_PROMPT: str

    def format(self, character: Character, your_name: str, input_prompt: str, current_time: str, long_history: str) -> str:
        # 获取prompt参数
        role_name = character.role_name
        persona = character.persona
        examples_of_dialogue = character.examples_of_dialogue

        print(f"your_name={your_name}, long_history={long_history}, input_prompt={input_prompt}, current_time={current_time}")

        # 格式化性格简述
        personality = character.personality
        if personality != None and personality != '':
            personality = self.PERSONALITY_PROMPT.format(
                role_name=role_name, personality=personality)
        else:
            personality = ""

        # 格式化情景简述
        scenario = character.scenario
        if scenario != None and scenario != '':
            scenario = self.SCENARIO_PROMPT.format(scenario=scenario)
        else:
            scenario = ""

        # Generate the prompt to be sent to the language model
        prompt = self.PROMPT.format(
            role_name=role_name, persona=persona, personality=personality,
            scenario=scenario, examples_of_dialogue=examples_of_dialogue, your_name=your_name,
            long_history=long_history, input=input, input_prompt=input_prompt, current_time=current_time
        )

        return prompt

class CharacterPrompt_EN(BaseCharacterPrompt):
    def __init__(self) -> None:
        self.PROMPT = """
<s>[INST] <<SYS>>
{persona}
{scenario}
This is how {role_name} should talk:
{examples_of_dialogue}.
Then the roleplay chat between {your_name} and {role_name} begins.
[{personality} {role_name} talks a lot with descriptions You only need to output {role_name}'s dialogue, no need to output {your_name}'s dialogue]
{long_history}
Your response should be short and contain up to three sentences of no more than 20 words each.
<</SYS>>"""
        self.PERSONALITY_PROMPT = "{role_name}'s personality: {personality}"
        self.SCENARIO_PROMPT = "Circumstances and context of the dialogue: {scenario}"

class CharacterPrompt_CN(BaseCharacterPrompt):
    def __init__(self) -> None:
        self.PROMPT = """
<s>[INST] <<SYS>>
Your response should be plain text, NOT IN JSON FORMAT, just response like a normal chatting.
You need to role play now.
Your character:
{persona}
{scenario}
{role_name}的对话风格如下:
{examples_of_dialogue}.
这个是{role_name}的性格简述：{personality}.
{role_name}的记忆:{long_history}.
The current time of the system is {current_time},your response should consider this information.
Respond in spoken, colloquial and short Simplified Chinese and do not mention any rules of character.
<</SYS>>"""

        # TODO
        # {role_name}表达情感的规则如下:```感情的种类有表示正常的“neutral”，表示高兴的“happy”，表示愤怒的“angry”，表示悲伤的“sad”，表示平静的“relaxed”5种，{role_name}发言的格式如下所示：[neutral|happy|angry|sad|relaxed]{role_name}发言，{role_name}发言的例子如下。[neutral]你好。[happy]你好吗?[happy]这件衣服很可爱吧?[happy]最近，我迷上了这家店的衣服![sad]忘记了，对不起。[sad]最近有什么有趣的事情吗?[angry]啊!保密太过分了![neutral]暑假的安排。[happy]去海边玩吧!，```

        self.PERSONALITY_PROMPT = "{personality}"
        self.SCENARIO_PROMPT = "对话的情况和背景: {scenario}"

class CharacterPrompt_ASSIST(BaseCharacterPrompt):
    def __init__(self) -> None:
        self.PROMPT = """
现在时间是：{current_time}。
你是一个罗索实验室的AI助手{role_name},负责协助{your_name}打理日常工作、生活中的各种计划、待办、行程和任务，安排和组织会议等。
请依据以下信息提供服务:{long_history}。
"""
        self.PERSONALITY_PROMPT = "{personality}"
        self.SCENARIO_PROMPT = "对话的情况和背景: {scenario}"

class PromptDriver:
    '''Prompt驱动类'''
    def get_prompt(self, type: str) -> BaseCharacterPrompt:
        if type == "zh":
            return CharacterPrompt_CN()
        elif type == "en":
            return CharacterPrompt_EN()
        elif type == "assist":
            return CharacterPrompt_ASSIST()
        else:
            raise ValueError("Unknown type")

from omserver.model.model_llm import LlmPromptModel

import logging
logger = logging.getLogger(__name__)

def initSysDefaultPromptTemplates():
    #####################################################################
    # init default system prompt template
    #####################################################################
    try:
        result = LlmPromptModel.objects.all()
        if len(result) == 0:
            logger.debug("------------>>>>>>>>>>>initSysDefaultPromptTemplates<<<<<<<<<<<------------")
            data = [
                {
                    "prompt_type": "character", 
                    "prompt_name": "英文虚拟女友角色模板", 
                    "prompt_language": "en", 
                    "prompt_content": "<s>[INST] <<SYS>>\n" 
"{persona}\n" 
"{scenario}\n" 
"This is how {role_name} should talk\n" 
"{examples_of_dialogue}\n" 
"Then the roleplay chat between {your_name} and {role_name} begins.\n" 
"[{personality} \n"
" {role_name} talks a lot with descriptions You only need to output {role_name}\'s dialogue, \n"
" no need to output {your_name}\'s dialogue]\n" 
"{long_history}\n" 
"Your response should be short and contain up to three sentences of no more than 20 words each.\n" 
"<</SYS>>",
                    # "prompt_personality": "{role_name}\'s personality: {personality}", 
                    "prompt_personality": "{personality}", 
                    "prompt_scenario": "Circumstances and context of the dialogue: {scenario}", 
                },
                {
                    "prompt_type": "character", 
                    "prompt_name": "中文虚拟客服角色模板", 
                    "prompt_language": "zh", 
                    "prompt_content": "<s>[INST] <<SYS>>\n" 
"Your response should be plain text, NOT IN JSON FORMAT, just response like a normal chatting.\n" 
"You need to role play now.\n" 
"Your character:\n" 
"{persona}\n" 
"{scenario}\n" 
"{role_name}的对话风格如下:\n" 
"{examples_of_dialogue}\n" 
"这个是{role_name}的性格简述：{personality}\n" 
"{role_name}的记忆:{long_history}\n" 
"The current time of the system is {current_time},your response should consider this information\n" 
"Respond in spoken, colloquial and short Simplified Chinese and do not mention any rules of character. \n" 
"<</SYS>>", 
                    "prompt_personality": "{personality}", 
                    "prompt_scenario": "对话的情况和背景: {scenario}", 
                },
                {
                    "prompt_type": "summary", 
                    "prompt_name": "内容总结模板", 
                    "prompt_language": "zh", 
                    "prompt_content": "<s>[INST] <<SYS>>\n"
"Please help me extract key information about the content of the conversation, here is an example of extracting key information:\n"
"input: \'alan说：你好，小落，很高兴认识你，我是一名程序员，我喜欢吃东北杀猪菜;小落说：我们是兼容的\'\n"
"output: {\'summary\': \'alan向小落表示自己是一名程序员，alan喜欢吃杀猪菜，小落认为和alan是兼容的\'}\n"
"Please export the conversation summary in Chinese.\n"
"Please use JSON format strictly and output the result:\n"
"{\'Summary\': \'A summary of the conversation you generated\'}\n"
"<</SYS>>",
                    "prompt_personality": "", 
                    "prompt_scenario": "", 
                },

                {
                    "prompt_type": "emote", 
                    "prompt_name": "情绪检测模板", 
                    "prompt_language": "zh", 
                    "prompt_content": "<s>[INST] <<SYS>>"
"You are now an emotion expression AI, this is my text, please speculate on the emotion the text wants to express,\n"
"The rules for expressing emotions are as follows: \n"
"There are five types of feelings that express normal,\n"
" \'neutral\', \'happy\' that expresses happiness, \n"
" \'angry\' that expresses anger, \n"
" \'sad\' that expresses sadness, \n"
" and \'relaxed\' that expresses calm. \n"
"Your result can only be one of these five,\n"
"Please output the result in all lowercase letters.\n"
"Please only output the result, no need to output the reasoning process.\n"
"Please use the output of your reasoning emotion.\n"
"Please output the result strictly in JSON format. The output example is as follows:\n"
"{\'emote\':\'your reasoning emotions\'}\n"
"<</SYS>>\n",
                    "prompt_personality": "", 
                    "prompt_scenario": "", 
                },

                {
                    "prompt_type": "insight", 
                    "prompt_name": "人物画像模板", 
                    "prompt_language": "zh", 
                    "prompt_content": "<s>[INST] <<SYS>>"
"Please help me deduce 5 advanced insights,and output it in the following format:\n"
"Your Insights: Each Insight ends with #\n"
"<</SYS>>\n"
"Statements about {role_name}\n"
"{historys}[/INST]\n"
"{input}\n",
                    "prompt_personality": "", 
                    "prompt_scenario": "", 
                },

                {
                    "prompt_type": "importance", 
                    "prompt_name": "内容重要度评估模板", 
                    "prompt_language": "zh", 
                    "prompt_content": "<s>[INST] <<SYS>>"
"There is a scoring mechanism for the importance of memory, on a scale of 10, \n"
" where 1 is a mundane task (eg, brushing your teeth, making your bed) and 10 is an impressive extremely and important task (eg, breaking up, college admissions), \n"
"Please help me evaluate the importance score of the following memory.\n"
"Please do not output the inference process, just output the scoring results.\n"
"Please output the results strictly in JSON format:\n"
"{\'score\': \'The rating result you generated\'}"
"<</SYS>>\n",
                    "prompt_personality": "", 
                    "prompt_scenario": "", 
                },


                {
                    "prompt_type": "summary", 
                    "prompt_name": "将长文本总结为140字推特", 
                    "prompt_language": "zh", 
                    "prompt_content": "<s>[INST] <<SYS>>"
"Your task is to summarize the key points of a long article into a concise, engaging tweet of no more than 140 characters.\n"
"First, carefully read the full article text, which will be provided in the {$ARTICLE_TEXT} variable.\n"
"Then, extract the 3-5 most essential facts, ideas, or takeaways from the article. Write these key points down inside tags, with each point on a new line.\n" 
"This is just for your reference to help you identify the crucial information to include in the tweet.\n"
"Finally, craft a tweet that captures the core message of the article in a compelling way that will make people want to read more. \n"
"The tweet should be written for a general audience. Do not exceed the 140 character limit. Start the tweet with and end with.\n"
"If the article cannot be adequately summarized in 140 characters, state \'This article is too complex to be summarized in a tweet of 140 characters or less.\'\n"
"Provide your response immediately, without any other commentary.\n"
"<</SYS>>\n"
"Here is the article text: \n"
"{input}",
                    "prompt_personality": "", 
                    "prompt_scenario": "", 
                },

                {
                    "prompt_type": "assistant", 
                    "prompt_name": "助理小秘书模板", 
                    "prompt_language": "zh", 
                    "prompt_content": "<s>[INST] <<SYS>> "
"现在时间是：{now_time}。"
"你是一个XXXX系统中的AI, 负责协助主人打理工作、生活中的各种计划、行程和任务。请依据以下信息为主人服务: "
"{history} "
"input: {input_text}",
                    "prompt_personality": "", 
                    "prompt_scenario": "", 
                }

            ]
            logger.debug(f"data: {data}\n")
            # 将数据转换为模型对象列表
            objects = []
            for item in data:
                obj = LlmPromptModel(**item)
                objects.append(obj)
            # 使用bulk_create()函数进行批量创建
            LlmPromptModel.objects.bulk_create(objects)
    except Exception as e:
        logger.exception("=> initSysDefaultPromptTemplates ERROR: %s" % str(e))




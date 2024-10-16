from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import redirect, render

from ..model.model_llm import LlmPromptModel
from ..mainservice import singleton_main_service
# from ..config import singleton_sys_config
from ..serializers import LlmPromptSerializer
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

import logging
import json

logger = logging.getLogger(__name__)

prompt_type_options = [
    {"id": 1, "prompt_type": "character", "desc": "角色类提示词"},
    {"id": 2, "prompt_type": "summary", "desc": "内容总结提示词"},
    {"id": 3, "prompt_type": "emote", "desc": "情绪检测提示词"},
    {"id": 4, "prompt_type": "insight", "desc": "内容摘要提示词"},
    {"id": 5, "prompt_type": "importance", "desc": "重要度判断提示词"},
]


from omserver.model.model import CSysConfigModel
sys_code = "adminSettings"


#####################################
## API
#####################################
@api_view(['POST'])
def chat(request):
    '''
    聊天
    :param request:
    :return:
    '''
    data = json.loads(request.body.decode('utf-8'))

    # 暂未实现用户模块，先写死用超级用户
    # is_login = request.session["is_login"]
    # user_name = request.session["user_name"]
    # user_id = request.session["user_id"]
    user_id = request.user.id
    user_name = request.user.username

    logger.debug("-----------------------------------------------------")
    logger.debug(f"user_id={user_id}, user_name={user_name}, json={data}")
    logger.debug("-----------------------------------------------------")

    # 解析url query string 参数
    query = data["query"]
    role_id = data["role_id"]
    your_name = data["your_name"]

    if isinstance(data, dict) and "type" in data.keys():
        llmtype = data["type"]
    else:
        llmtype = ""

    if isinstance(data, dict) and "kb_id" in data.keys():
        kb_id = data["kb_id"]
    else:
        kb_id = "0"

    if user_id == None and user_name == "":
        user_id = 1
        user_name = "Anonymous"
        user_name = your_name

    singleton_main_service.chat(role_id=role_id, your_name=user_name, query=query, llmtype=llmtype, kb_id=kb_id, user_id=user_id)

    return Response({"response": "OK", "code": "200"})


@login_required
@api_view(['GET', 'POST'])
def llm_settings(request):
  if request.method == "GET":
    user_id = request.session.get("user_id")
    session_cfg = request.session.get("cfg")

    sys_cfg_json = json.loads(session_cfg)

    context = {
        "OPENAI_API_KEY": sys_cfg_json["languageModelConfig"]["openai"]["OPENAI_API_KEY"],
        "OPENAI_BASE_URL": sys_cfg_json["languageModelConfig"]["openai"]["OPENAI_BASE_URL"],
        "OPENAI_MODEL": sys_cfg_json["languageModelConfig"]["openai"]["OPENAI_MODEL"],
        }
    
    logger.debug(f"=> context = {context}")

    return render(request, "llm_settings.html", context)
  else:
    # try:
      print("---------------------------------------------------------------")
      user_id = request.session.get("user_id")
      session_cfg = request.session.get("cfg")

      data = request.data

      print(f"llm_settings===>>> request.user.is_authenticated={request.user.is_authenticated}")  # True表示存在此用户，
      print(f"llm_settings===>>> request.user={request.user}")  # 没有登录显示：AnonymousUser匿名用户    登录显示登录的用户对象数据
      print(f"llm_settings===>>> request.user.is_superuser={request.user.is_superuser}")
      print(f"llm_settings===>>> user_id={user_id}, cfg={session_cfg}")
      print(f"llm_settings===>>> data={data}")

      OPENAI_API_KEY = request.data.get('OPENAI_API_KEY')
      OPENAI_BASE_URL = request.data.get('OPENAI_BASE_URL')
      OPENAI_MODEL = request.data.get('OPENAI_MODEL')
      print(f"llm_settings===>>> OPENAI_API_KEY={OPENAI_API_KEY}, OPENAI_BASE_URL={OPENAI_BASE_URL}, OPENAI_MODEL={OPENAI_MODEL}")

      sys_cfg_json = json.loads(session_cfg)

      cfg = CSysConfigModel.objects.get(code=sys_code, user_id=user_id)
      if cfg == None:
        logger.debug("=> save default sys config to db")
        sys_cfg_json["languageModelConfig"]["openai"]["OPENAI_API_KEY"] = OPENAI_API_KEY
        sys_cfg_json["languageModelConfig"]["openai"]["OPENAI_BASE_URL"] = OPENAI_BASE_URL
        sys_cfg_json["languageModelConfig"]["openai"]["OPENAI_MODEL"] = OPENAI_MODEL
        sys_config_model = CSysConfigModel(code=sys_code, config=json.dumps(sys_cfg_json), user_id=user_id)
        sys_config_model.save()
      else:
        logger.debug(f"=> update cfg to database")
        sys_cfg_json = json.loads(cfg.config)
        sys_cfg_json["languageModelConfig"]["openai"]["OPENAI_API_KEY"] = OPENAI_API_KEY
        sys_cfg_json["languageModelConfig"]["openai"]["OPENAI_BASE_URL"] = OPENAI_BASE_URL
        sys_cfg_json["languageModelConfig"]["openai"]["OPENAI_MODEL"] = OPENAI_MODEL
        cfg.config = str(json.dumps(sys_cfg_json))
        cfg.save()

      logger.debug("---------------------------------------------------------------")
      logger.debug(f"llm_settings===>>> config={json.dumps(sys_cfg_json)}")
      logger.debug("---------------------------------------------------------------")

      request.session["cfg"] = json.dumps(sys_cfg_json)
      logger.debug("---------------------------------------------------------------")

      return Response({"response": "ok", "code": "200"})
    
    # except Exception as e:
    #   logger.debug("=> load sys config error: %s" % str(e))
    #   return Response({"response": str(e), "code": "500"})

@login_required
def llm_chat(request):
    return render(request, "llm_chat.html")

@login_required
def llm_prompt(request):
    llm_prompt = LlmPromptModel.objects.all()
    llm_prompt_list = serialize('json', llm_prompt)
    j = json.loads(llm_prompt_list)

    context = {"llm_prompt": json.dumps(j)}

    logger.debug(f"llm_prompt=>{context}")

    return render(request, "llm_prompt.html", context)

@login_required
def llm_kb(request):
    return render(request, "llm_kb.html")

@login_required
def llm_bing_qa(request):
    return render(request, "llm_bing_qa.html")

@api_view(['POST','GET'])
def llm_prompt_new(request):
    print(f"request.user.is_authenticated={request.user.is_authenticated}")  # True表示存在此用户，
    print(f"request.user={request.user}")  # 没有登录显示：AnonymousUser匿名用户    登录显示登录的用户对象数据
    print(f"request.user.is_superuser={request.user.is_superuser}")

    if request.method == "POST":
        data = []

        try:
            data = request.data
            logger.debug(f"llm_prompt_add-->>data={data}")
        except Exception as e:
            logger.debug("=> llm_prompt_new 4 ERROR: %s" % str(e))

        serializer = LlmPromptSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"response": "ok", "code": "200"})
        logger.error(serializer.errors)

        return Response({"response": "no", "code": "500"})

        # prompt_name = data.get('prompt_name')
        # prompt_type = data.get('prompt_type')
        # prompt_language = data.get('prompt_language')
        # prompt_content = data.get('prompt_content')
        # prompt_personality = data.get('prompt_personality')
        # prompt_scenario = data.get('prompt_scenario')

        # logger.debug(f"llm_prompt_add-->>prompt_name={prompt_name}")

        # # 新增 LlmPromptModel 实例并保存到数据库
        # llm_prompt = LlmPromptModel(
        #     prompt_name=prompt_name,
        #     prompt_type = prompt_type,
        #     prompt_language = prompt_language,
        #     prompt_content=prompt_content,
        #     prompt_personality=prompt_personality,
        #     prompt_scenario=prompt_scenario
        # )
        # llm_prompt.save()
        # 
        # return Response({"response": "ok", "code": "200"})
    else:
        context = {"prompt_type_list": prompt_type_options}
        return render(request, "llm_prompt_add.html", context)

@api_view(['POST','GET'])
def llm_prompt_modify(request, pk):
    if request.method == "POST":
        data = []
        # 修改数据
        data = request.data

        id = pk
        prompt_name = data.get('prompt_name')
        prompt_type = data.get('prompt_type')
        prompt_language = data.get('prompt_language')
        prompt_content = data.get('prompt_content')
        prompt_personality = data.get('prompt_personality')
        prompt_scenario = data.get('prompt_scenario')

        # 更新 LlmPromptModel 实例并保存到数据库
        llm_prompt = LlmPromptModel(
            id=id,
            prompt_name=prompt_name,
            prompt_type = prompt_type,
            prompt_language = prompt_language,
            prompt_content=prompt_content,
            prompt_personality=prompt_personality,
            prompt_scenario=prompt_scenario
        )
        llm_prompt.save()

        return Response({"response": "ok", "code": "200"})
    else:
        prompt = LlmPromptModel.objects.filter(pk=pk)
        prompt_serialzed = serialize('json', prompt)
        j = json.loads(prompt_serialzed)

        logger.debug(f"prompt_list={prompt_serialzed}")

        context = {"prompt_type_list": prompt_type_options, "prompt": json.dumps(j)}

        return render(request, "llm_prompt_modify.html", context)

@csrf_exempt
@api_view(['POST'])
def llm_prompt_delete(request, pk):
    print(f"llm_prompt_delete-->>pk={pk}")
    # 删除数据
    llm_prompt_model = get_object_or_404(LlmPromptModel, pk=pk)
    print(f"llm_prompt_model={llm_prompt_model}")
    if llm_prompt_model:
        llm_prompt_model.delete()
        
    print(f"prompt_type_options={prompt_type_options}")
    return Response({"response": prompt_type_options, "code": "200"});

@api_view(['GET'])
def llm_prompt_type_list(request):
    print(f"prompt_type_options={prompt_type_options}")
    return Response({"response": prompt_type_options, "code": "200"});

@api_view(['GET'])
def llm_kb_list(request):
    kb_options = [
        {"kb_id": 0, "kb_name": "----选择知识库----"},
        {"kb_id": 1, "kb_name": "小科会议助手"},
        {"kb_id": 2, "kb_name": "问问-I模块"},
        {"kb_id": 3, "kb_name": "问问-RTCSDK"},
    ]
    
    return Response({"response": kb_options, "code": "200"});

""" 
@api_view(['GET'])
def chatlog_list(request):
    result = ChatlogModel.objects.all()
    serializer = ChatlogSerializer(data=result, many=True)
    serializer.is_valid()
    result = serializer.data
    return Response({"response": result, "code": "200"})


@api_view(['GET'])
def chatlog_detail(request, pk):
    role = get_object_or_404(ChatlogModel, pk=pk)
    return Response({"response": role, "code": "200"})


def chatlog_save(chat_id: int, chat_user: str, chat_content: str, chat_emotion: str, chat_llm_type: str, chat_kb_id: str, chat_src_ip: str, chat_answer_audio: str, chat_timestamp: str):
    chatlog = ChatlogModel(
        chat_id=chat_id,
        chat_user=chat_user,
        chat_content=chat_content,
        chat_emotion=chat_emotion,
        chat_llm_type=chat_llm_type,
        chat_kb_id=chat_kb_id,
        chat_src_ip=chat_src_ip,
        chat_timestamp=datetime.datetime.now().isoformat(),
        chat_answer_audio=chat_answer_audio,
    )
    chatlog.save()
    return True


def chatlog_save2(cl: Chatlog):
    # 创建 CustomRoleModel 实例并保存到数据库
    chatlog = ChatlogModel(
        chat_id=cl.chat_id,
        chat_user=cl.chat_user,
        chat_content=cl.chat_content,
        chat_emotion=cl.chat_emotion,
        chat_llm_type=cl.chat_llm_type,
        chat_kb_id=cl.chat_kb_id,
        chat_src_ip=cl.chat_src_ip,
        chat_timestamp=datetime.datetime.now().isoformat(),
        chat_answer_audio=cl.chat_answer_audio,
    )
    chatlog.save()
    return True


@api_view(['POST'])
def chatlog_add(request):
    data = request.data  # 获取请求的 JSON 数据

    # 从 JSON 数据中提取字段值
    chat_id = data.get('chat_id')
    chat_user = data.get('role_name')
    chat_content = data.get('chat_content')
    chat_emotion = data.get('chat_emotion')
    chat_llm_type = data.get('chat_llm_type')
    chat_kb_id = data.get('chat_kb_id')
    chat_src_ip = data.get('chat_src_ip')
    chat_answer_audio = data.get('chat_answer_audio')

    # 创建 CustomRoleModel 实例并保存到数据库
    success = chatlog_save(
        chat_id=chat_id,
        chat_user=chat_user,
        chat_content=chat_content,
        chat_emotion=chat_emotion,
        chat_llm_type=chat_llm_type,
        chat_kb_id=chat_kb_id,
        chat_src_ip=chat_src_ip,
        chat_timestamp=datetime.datetime.now().isoformat(),
        chat_answer_audio=chat_answer_audio,
    )
    
    if success:
        return Response({"response": "Data added to database", "code": "200"})
    else:
        return Response({"response": "Error occured while saving data database", "code": "500"})


@api_view(['POST'])
def chatlog_edit(request, pk):
    data = request.data  # 获取请求的 JSON 数据

    # 从 JSON 数据中提取字段值
    chat_id = data.get('chat_id')
    chat_user = data.get('role_name')
    chat_content = data.get('chat_content')
    chat_emotion = data.get('chat_emotion')
    chat_llm_type = data.get('chat_llm_type')
    chat_kb_id = data.get('chat_kb_id')
    chat_src_ip = data.get('chat_src_ip')
    chat_answer_audio = data.get('chat_answer_audio')

    # 更新 CustomRoleModel 实例并保存到数据库
    custom_role = ChatlogModel(
        chat_id=chat_id,
        chat_user=chat_user,
        chat_content=chat_content,
        chat_emotion=chat_emotion,
        chat_llm_type=chat_llm_type,
        chat_kb_id=chat_kb_id,
        chat_src_ip=chat_src_ip,
        chat_answer_audio=chat_answer_audio
    )
    custom_role.save()
    return Response({"response": "Data edit to database", "code": "200"})

@api_view(['POST'])
def chatlog_delete(request, pk):
    role = get_object_or_404(ChatlogModel, pk=pk)
    role.delete()
    return Response({"response": "ok", "code": "200"})


if __name__ == '__main__':
    print("111")
    
    chatlog_save("", "aa", "test content", "", "om_llm", "rtcsdk", "", "", "")
    print("222")
    session = chatlog_list(None)

    print("333")
"""

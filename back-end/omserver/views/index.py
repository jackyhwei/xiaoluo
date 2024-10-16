from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.conf import settings
from django.core.serializers import serialize
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from ..config import singleton_sys_config
from omserver.model.model_character import CharacterRoleModel

import json
import logging

logger = logging.getLogger(__name__)

@login_required
def main(request):

    user_id = request.user.id
    user_name = request.user.username

    print(f"request.user.username={request.user.username}")
    print(f"user_id={user_id}")
    print(f"request.user.is_authenticated={request.user.is_authenticated}")  # True表示存在此用户，
    print(f"request.user={request.user}")  # 没有登录显示：AnonymousUser匿名用户    登录显示登录的用户对象数据

    context = {"version": "0.1.2", "username": user_name}

    return render(request, "index.html", context)

def syscfg(request):
    return render(request, "syscfg.html")

@api_view(['POST'])
def save_config(request):
    '''
      保存系统配置
    :param request:
    :return:
    '''
    data = json.loads(request.body.decode('utf-8'))
    config = data["config"]
    singleton_sys_config.save(config)
    singleton_sys_config.load()
    return Response({"response": config, "code": "200"})

def listToJson(lst):
    import json
    import numpy as np
    keys = [str(x) for x in np.arange(len(lst))]
    list_json = dict(zip(keys, lst))
    str_json = json.dumps(list_json, indent=2, ensure_ascii=False)  # json转为string
    print(f"str_json={str_json}")
    return list_json

from django.contrib.auth.models import User
from omserver.model.model import CSysConfigModel

@api_view(['GET'])
def get_config(request):
    '''
      获取系统配置
    :param request:
    :return:
    '''
    print(f"character_model_add===>>> request.user.is_authenticated={request.user.is_authenticated}")  # True表示存在此用户，
    print(f"character_model_add===>>>request.user={request.user}")  # 没有登录显示：AnonymousUser匿名用户    登录显示登录的用户对象数据
    print(f"character_model_add===>>>request.user.is_superuser={request.user.is_superuser}")

    user_name = request.user
    sys_config_json = []

    logger.debug("-----------------------------------------------------")
    try:
      user = User.objects.get(username=user_name)
      userid = user.id
      cfg = CSysConfigModel.objects.get(user_id=userid, code="adminSettings")
      logger.debug(f"---------->>>>>>>> loading cfg for user={userid}")
      if cfg == None:
          logger.error(f"can not find cfg for user={userid}, use default cfg")
          sys_config_json = singleton_sys_config.get()
      else:
          sys_config_json = json.loads(cfg.config)
    except User.DoesNotExist:
      print("can not find specified user, use default cfg")
      # load sys config
      sys_config_json = singleton_sys_config.get()

    logger.debug(f"sys_config_json={json.dumps(sys_config_json)}")

    role_id = request.query_params.get('roleid', '1')
    logger.debug("-----------------------------------------------------")
    logger.debug(f"---------->>>>>>>> loading character role={role_id}")

    # load character by the specified role_id
    role = CharacterRoleModel.objects.filter(id=role_id)
    if len(role) == 0:
      print(f"can not find specified role: {role_id}")
    else:
      role_str = serialize('json', role)

      print("-->>>>character_model_list: ", role_str)
      j = json.loads(role_str)

      print(f"j: {json.dumps(j)}")

      id = j[0]["pk"]
      role_name = j[0]["fields"]["role_name"]
      gender = j[0]["fields"]["gender"]
      model_id = j[0]["fields"]["model_id"]
      voice_id = j[0]["fields"]["voice_id"]
      scene_id = j[0]["fields"]["scene_id"]
      template_type = j[0]["fields"]["custom_role_template_type"]

      print(f'-->>>>>id={id}, role_name={role_name}, voice_Id={voice_id}, scene_id={scene_id}, template_type={template_type}')
      sys_config_json["characterConfig"]["character"] = id
      sys_config_json["characterConfig"]["character_name"] = role_name
      sys_config_json["characterConfig"]["character_gender"] = gender
      sys_config_json["characterConfig"]["vrmModel"] = model_id
      sys_config_json["characterConfig"]["background_id"] = scene_id
      sys_config_json["characterConfig"]["background_url"] = scene_id
      sys_config_json["characterConfig"]["ttsConfig"]["ttsVoiceId"] = voice_id
      sys_config_json["characterConfig"]["custom_role_template_type"] = template_type

    logger.debug("-----------------------------------------------------")
    logger.debug(f"---------->>>>>>>> final cfg={json.dumps(sys_config_json)}")

    # return Response({"response": json.dumps(sys_config_json), "code": "200"})
    return Response({"response": sys_config_json, "code": "200"})

def test_vrm(request):
    return render(request, 'test_vrm.html')

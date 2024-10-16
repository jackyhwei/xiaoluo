from django.conf import Settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
import json


from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..config import singleton_sys_config

from ..omengine.reflection.reflection_generation import ReflectionGeneration

import json
import time

from ..model.model_llm import LlmLocalMemoryModel
from django.core.serializers import serialize
from rest_framework.response import Response

#####################################
## frontend
#####################################
@login_required
def view_shorttime_list(request):
    data = LlmLocalMemoryModel.objects.all()
    jsonData = serialize('json', data)
    print(jsonData)
    j = json.loads(jsonData)
    print("json: " + json.dumps(j))
    return render(request, "memory_shorttime.html", {"memory_shorttime_list": json.dumps(j)})

@login_required
def view_longtime_list(request):
    j = {}
    print("json: " + json.dumps(j))
    return render(request, "memory_longtime.html", {"memory_longtime_list": json.dumps(j)})

def api_shorttime_list():
    data = LlmLocalMemoryModel.objects.all()
    jsonData = serialize('json', data)
    j = json.loads(jsonData)

    print("json: " + json.dumps(j))
 
    return Response({"response": json.dumps(j), "code": "200"})


#####################################
## API
#####################################
def api_shorttime_delete(request, pk):
    # 删除数据
    data = get_object_or_404(LlmLocalMemoryModel, pk=pk)
    data.delete()

    return Response({"response": "ok", "code": "200"})

@api_view(['GET'])
def api_longtime_list():
    j = {}
    return Response({"response": json.dumps(j), "code": "200"})

def api_longtime_delete(request, pk):
    # 删除数据
    return Response({"response": "ok", "code": "200"})

@api_view(['GET'])
def reflection_generation(request):
    '''
      生成新记忆
    :return:
    '''
    rg = ReflectionGeneration()
    rg.generation(role_name="Maiko")
    timestamp = time.time()
    expr = f'timestamp <= {timestamp}'
    result = singleton_sys_config.memory_storage_driver.pageQuery(1, 100, expr=expr)
    return Response({"response": result, "code": "200"})


@api_view(['GET'])
def clear_memory(request):
    '''
      删除测试记忆
    :return:
    '''
    result = singleton_sys_config.memory_storage_driver.clear("alan")
    return Response({"response": result, "code": "200"})





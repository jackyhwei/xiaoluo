from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.decorators import method_decorator

from omserver.model.model_character import CharacterRoleModel, CharacterActionModel, CharacterEmotionModel, CharacterModelModel, CharacterRoleTemplateModel
from omserver.model.model import BackgroundImageModel
from omserver.model.model_tts import TtsVoiceIdModel
from omserver.serializers import CharacterActionSerializer, CharacterEmotionSerializer, CharacterRoleSerializer, CharacterModelSerializer
from omserver.model.model_character import CharacterActionModel, CharacterEmotionModel, CharacterRoleModel, CharacterModelModel

import os
import json
import logging

logger = logging.getLogger(__name__)


#######################################################################
#######################################################################
class CharacterAction:
    '''character action
    ''' 
    @login_required
    def character_action_store(request):
        character_action = CharacterActionModel.objects.all()
        character_action_list = serialize('json', character_action)
        j = json.loads(character_action_list)
        context = {'character_action_list': json.dumps(j)}
        logger.debug(json.dumps(j))
        return render(request, "character_action_store.html", context)
    
    @login_required
    def character_actions(request):
        character_action = CharacterActionModel.objects.all()
        character_action_list = serialize('json', character_action)
        j = json.loads(character_action_list)
        context = {'character_action_list': json.dumps(j)}

        logger.debug(json.dumps(j))

        return render(request, "character_actions.html", context)

    @login_required
    def character_action_detail(request, pk):
        # load action
        action = CharacterActionModel.objects.filter(pk=pk)
        action_serialzed = serialize('json', action)
        j = json.loads(action_serialzed)

        logger.debug(f"action={action_serialzed}")

        context = {
            "character_action": json.dumps(j),
        }
        return render(request, "character_action_detail.html", context)
    
    @login_required
    @api_view(['POST', 'GET'])
    def character_action_modify(request, pk):
        if request.method == "GET":
            # load action
            action = CharacterActionModel.objects.filter(pk=pk)
            action_serialzed = serialize('json', action)
            j = json.loads(action_serialzed)

            logger.debug(f"action={action_serialzed}")

            context = {
                "character_action": json.dumps(j),
                'user_id': 1
            }

            return render(request, "character_action_modify.html", context)
        else:
            logger.debug(f"character_action_modify in, data={request.data}")
            action_name = request.data["action_name"]
            action_status = request.data["status"]
            action_gender = request.data["action_gender"]
            action_memo = request.data["memo"]
            permission = request.data["permission"]

            # if hasattr(request.data, 'action_avatar'):
            if request.data.__contains__("action_avatar"):
                action_avatar = request.data["action_avatar"]
                print("------------------------------------------------------")
            else:
                action_avatar = ""
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            try:
                action = CharacterActionModel.objects.get(id=pk)
                logger.debug(f"start to update action: {action_name}, typeof action_avatar: {type(action_avatar)}")
                action.action_name = action_name
                action.status = action_status
                action.action_gender = action_gender
                action.memo = action_memo
                action.permission = permission

                # 用户并未上传新的缩略图就不更新
                if action_avatar != "":
                    # 删除关联的文件
                    old_avatar = str(action.action_avatar)
                    logger.debug(f"new thumnail, old={str(old_avatar)}, new={str(action_avatar)}")
                    if old_avatar != "":
                        old_avatar = os.path.join(settings.MEDIA_ROOT, str(action.action_avatar))
                        logger.warn(f"try remove old avatar: {old_avatar}")
                        if os.path.exists(old_avatar):
                            os.remove(old_avatar)
                            logger.debug(f"old avatar image removed: {old_avatar}")
                    action.action_avatar = action_avatar

                action.save()

                logger.debug(f"action modified successfully, pk={pk}, action name={action_name}")
                return Response({"response": "modify action ok", "code": "200"})
            except CharacterActionModel.DoesNotExist as e:
                logger.error(f"action modify failed, pk={pk} not exists, error={str(e)}")
                return Response({"response": "no", "code": "500"})

    @api_view(['POST', 'GET'])
    def character_action_create(request):
        if request.method == "GET":
            context = {'user_id': 1, "id": 0}
            return render(request, "character_action_add.html", context)
        else:
            serializer = CharacterActionSerializer(data=request.data)
            logger.debug(f"character_action_create==============>data:{request.data}")
            if serializer.is_valid():
                # 获取上传文件对象
                uploaded_file = request.data['action_model']
                original_filename = uploaded_file.name
                serializer.save()
                logger.debug(f"character_action_create successfully, file name={original_filename}")
                return Response({"response": "ok", "code": "200"})
            logger.error(serializer.errors)
            return Response({"response": "no", "code": "500"})

    @api_view(['GET'])
    def character_action_list(request):
        action_list = CharacterActionModel.objects.filter(status=1)
        serializer = CharacterActionSerializer(action_list, many=True)
        logger.debug(f"action list: {serializer.data}")
        return Response({"response": serializer.data, "code": "200"})

    @api_view(['POST'])
    def character_action_delete(request,pk):
        # 删除数据
        action = get_object_or_404(CharacterActionModel, pk=pk)
        action.delete()

        return Response({"response": "ok", "code": "200"})

    @api_view(['POST'])
    def character_action_enable(request,pk):
        data = request.data  # 获取请求的 JSON 数据
        # 从 JSON 数据中提取字段值
        status = data.get('status')

        # 更新 CharacterActionModel 实例并保存到数据库
        action = CharacterActionModel.objects.get(id=pk)
        action.status = int(status)
        action.save()

        return Response({"response": "enable/disabled action ok", "code": "200"})

#######################################################################
#######################################################################
class CharacterEmotion:
    '''character emotoin
    ''' 
    @login_required
    def character_emotions(request):
        character_emotion = CharacterEmotionModel.objects.all()
        character_emotion_list = serialize('json', character_emotion)
        j = json.loads(character_emotion_list)
        context = {'character_emotion_list': json.dumps(j)} 

        return render(request, "character_emotions.html", context)

    @api_view(['GET'])
    def character_emotion_list(request):
        emotion_list = CharacterEmotionModel.objects.filter(status=1)
        serializer = CharacterEmotionSerializer(emotion_list, many=True)
        return Response({"response": serializer.data, "code": "200"})

    @api_view(['POST'])
    def character_emotion_delete(request,pk):
        # 删除数据
        emotion = get_object_or_404(CharacterEmotionModel, pk=pk)
        emotion.delete()

        return Response({"response": "ok", "code": "200"})

    @api_view(['POST'])
    def character_emotion_enable(request,pk):
        print("=============================================")
        data = request.data  # 获取请求的 JSON 数据
        # 从 JSON 数据中提取字段值
        status = data.get('status')

        emotion = CharacterEmotionModel.objects.get(id=pk)
        emotion.status = int(status)
        emotion.save()

        return Response({"response": "enable/disabled emotion ok", "code": "200"})

#######################################################################
#######################################################################
class CharacterModel:
    '''character role model
    ''' 
    @login_required
    def character_models(request):
        character_model = CharacterModelModel.objects.all()
        character_model_list = serialize('json', character_model)

        logger.debug(f"-->>>>character_model_list: {character_model_list}")
        j = json.loads(character_model_list)

        context = {'character_model_list': json.dumps(j)}  # 将JSON数据转换为字符串
        return render(request, "character_models.html", context)

    @api_view(['POST'])
    def character_model_delete(request, pk):
        """
        删除VRM模型数据
        """
        # 删除数据
        vrm_model = get_object_or_404(CharacterModelModel, pk=pk)
        vrm_model.delete()

        # 获取要删除的文件路径
        file_path = os.path.join(settings.MEDIA_ROOT, str(vrm_model.vrm_url))
        # 删除关联的文件
        if os.path.exists(file_path):
            os.remove(file_path)

        return Response({"response": "ok", "code": "200"})


    @api_view(['POST','GET'])
    def character_model_add(request):
        if request.method == "GET":
            print(f"character_model_add===>>> request.user.is_authenticated={request.user.is_authenticated}")  # True表示存在此用户，
            print(f"character_model_add===>>>request.user={request.user}")  # 没有登录显示：AnonymousUser匿名用户    登录显示登录的用户对象数据
            print(f"character_model_add===>>>request.user.is_superuser={request.user.is_superuser}")

            user_id = request.user
            id = ""

            context = {"user_id": user_id, "id": id}
            return render(request, "character_models_add.html", context)
        else:
            """
            上传VRM模型
            """
            logger.debug(f"uploading new vrm model={request.data}")


            # # 将文件写入本地
            # f = open(file.name, 'wb')
            # for line in file.chunks():     # 由于文件不是一次性上传的，因此一块一块的写入
            #     f.write(line)
            # f.close()

            # logger.debug(f"========================================>>update vrm_url")

            data = request.data
            # data["vrm_url"] = file.name

            serializer = CharacterModelSerializer(data=data)
            if serializer.is_valid():
                # 获取上传文件对象
                uploaded_file = request.data['vrm_url']
                # uploaded_file = request.FILES.get('file')    # 获取文件对象，包括文件名文件大小和文件内容
                logger.debug(f"========================================>>save file, file={uploaded_file.name}, size={uploaded_file.size}")
                serializer.save(vrm_name=uploaded_file.name, vrm_type="user")
                return Response({"response": "ok", "code": "200"})
            logger.error(serializer.errors)
            return Response({"response": "HTTP 412 - 先决条件失败", "code": "412"})

    @api_view(['POST'])
    def character_model_upload(request):
        if request.method == "GET":
            return render(request, "character_models_add.html")
        else:
            """
            上传VRM模型
            """
            serializer = CharacterModelSerializer(data=request.data)
            if serializer.is_valid():
                # 获取上传文件对象
                uploaded_file = request.data['vrm']
                # 获取上传文件的原始文件名
                original_filename = uploaded_file.name
                serializer.save(original_name=original_filename, type="user")
                return Response({"response": "ok", "code": "200"})
            logger.error(serializer.errors)
            return Response({"response": "no", "code": "500"})

    @api_view(['GET'])
    def character_model_list(request):
        model_list = CharacterModelModel.objects.filter(status=1)
        serializer = CharacterModelSerializer(model_list, many=True)
        return Response({"response": serializer.data, "code": "200"})

    @api_view(['POST'])
    def character_model_enable(request,pk):
        data = request.data  # 获取请求的 JSON 数据
        # 从 JSON 数据中提取字段值
        status = data.get('status')

        # 更新 CharacterModelModel 实例并保存到数据库
        action = CharacterModelModel.objects.get(id=pk)
        action.status = int(status)
        action.save()

        return Response({"response": "enable/disabled 3d-model ok", "code": "200"})

#######################################################################
#######################################################################
class CharacterRoleTemplate:
    '''character role template
    ''' 
    @login_required
    def character_role_template(request):
        character_role = CharacterRoleTemplateModel.objects.all()
        character_role_list = serialize('json', character_role)

        logger.debug(f"role template --->>> {character_role_list}")

        j = json.loads(character_role_list)
        for item in j:
            a = item["fields"]["role_template_name"]
        logger.debug("json: " + json.dumps(j))

        return render(request, "character_role_template.html", {"character_role_template": json.dumps(j)})


#######################################################################
#######################################################################
class CharacterRole:
    '''character roles
    ''' 
    @login_required
    def character_store(request):
        character_role = CharacterRoleModel.objects.all()
        character_role_list = serialize('json', character_role)

        j = json.loads(character_role_list)

        return render(request, "character_store.html", {"character_custome_role": json.dumps(j)})

    @login_required
    @csrf_exempt
    def character_role_add(request):
        # load role template list
        templates = CharacterRoleTemplateModel.objects.all()
        templates_list = serialize('json', templates)
        j_templates = json.loads(templates_list)

        # load background list 
        bgimg = BackgroundImageModel.objects.all()
        bgimg_list = serialize('json', bgimg)
        j_bgimg = json.loads(bgimg_list)

        # load character mode list
        character_model = CharacterModelModel.objects.all()
        character_model_list = serialize('json', character_model)
        j_character_mode = json.loads(character_model_list)

        # load tts voiceId list
        voice_id = TtsVoiceIdModel.objects.all()
        voice_id_list = serialize('json', voice_id)
        j_voiceId = json.loads(voice_id_list)

        context = {
            "character_role_template": json.dumps(j_templates), 
            "background_image": json.dumps(j_bgimg), 
            "character_model": json.dumps(j_character_mode),
            "tts_voiceId": json.dumps(j_voiceId),
        }
        return render(request, "character_role_add.html", context)
    
    @login_required
    def character_role_modify(request):
        if request.method == "POST":
            pass
        else:
            role_id = request.GET.get("role")

            logger.debug(f"role_id={role_id}")

            # load role template list
            templates = CharacterRoleTemplateModel.objects.all()
            templates_list = serialize('json', templates)
            j_templates = json.loads(templates_list)

            # load background list 
            bgimg = BackgroundImageModel.objects.all()
            bgimg_list = serialize('json', bgimg)
            j_bgimg = json.loads(bgimg_list)

            # load character mode list
            character_model = CharacterModelModel.objects.all()
            character_model_list = serialize('json', character_model)
            j_character_mode = json.loads(character_model_list)

            # load tts voiceId list
            voice_id = TtsVoiceIdModel.objects.all()
            voice_id_list = serialize('json', voice_id)
            j_voiceId = json.loads(voice_id_list)

            # load character role
            role = CharacterRoleModel.objects.filter(pk=role_id)
            role_serialzed = serialize('json', role)
            j_role = json.loads(role_serialzed)

            logger.debug(f"role_serialzed={role_serialzed}")

            context = {
                "character_role": json.dumps(j_role),
                "character_role_template": json.dumps(j_templates), 
                "background_image": json.dumps(j_bgimg), 
                "character_model": json.dumps(j_character_mode),
                "tts_voiceId": json.dumps(j_voiceId),
            }
            return render(request, "character_role_modify.html", context)

    @api_view(['GET'])
    def character_role_list(request):
        result = CharacterRoleModel.objects.all()
        serializer = CharacterRoleSerializer(data=result, many=True)
        serializer.is_valid()
        result = serializer.data
        return Response({"response": result, "code": "200"})


    # @api_view(['GET'])
    # def character_role_detail(request, pk):
    #     role = get_object_or_404(CharacterRoleModel, pk=pk)
    #     return Response({"response": role, "code": "200"})

    @login_required
    @api_view(['GET'])
    def character_role_detail(request):
        print("-------------------------------------------------------------")
        role_id = request.GET.get("role")

        logger.debug(f"role_id={role_id}")

        # load role template list
        templates = CharacterRoleTemplateModel.objects.all()
        templates_list = serialize('json', templates)
        j_templates = json.loads(templates_list)

        # load background list 
        bgimg = BackgroundImageModel.objects.all()
        bgimg_list = serialize('json', bgimg)
        j_bgimg = json.loads(bgimg_list)

        # load character mode list
        character_model = CharacterModelModel.objects.all()
        character_model_list = serialize('json', character_model)
        j_character_mode = json.loads(character_model_list)

        # load tts voiceId list
        voice_id = TtsVoiceIdModel.objects.all()
        voice_id_list = serialize('json', voice_id)
        j_voiceId = json.loads(voice_id_list)

        # load character role
        role = CharacterRoleModel.objects.filter(pk=role_id)
        role_serialzed = serialize('json', role)
        j_role = json.loads(role_serialzed)

        logger.debug(f"role_serialzed={role_serialzed}")

        context = {
            "character_role": json.dumps(j_role),
            "character_role_template": json.dumps(j_templates), 
            "background_image": json.dumps(j_bgimg), 
            "character_model": json.dumps(j_character_mode),
            "tts_voiceId": json.dumps(j_voiceId),
        }

        return render(request, "character_role_detail.html", context)


    @method_decorator(csrf_protect, name='dispatch')
    class MyView(View):
        def post(self, request, *args, **kwargs):
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            # 检查CSRF token
            if not request.is_ajax() or not request.csrf_is_valid():
                return JsonResponse({'error': 'Invalid CSRF token'}, status=403)
            
            # 处理POST请求的逻辑
            # ...
            return JsonResponse({'message': 'POST request processed successfully.'})
    

    @api_view(['POST'])
    @csrf_exempt
    def character_role_create(request):
        data = request.data  # 获取请求的 JSON 数据
        print(f"==> character_role_create: data={data}")

        # 从 JSON 数据中提取字段值
        role_name = data.get('role_name')
        gender = data.get('gender')
        avatar = data.get('avatar')
        persona = data.get('persona')
        personality = data.get('personality')
        scenario = data.get('scenario')
        examples_of_dialogue = data.get('examples_of_dialogue')
        custom_role_template_type = data.get('custom_role_template_type')
        model_id = data.get('model_id')
        scene_id = data.get('scene_id')
        voice_id = data.get('voice_id')

        # 创建 CharacterRoleModel 实例并保存到数据库
        custom_role = CharacterRoleModel(
            role_name=role_name,
            gender=gender,
            avatar = avatar,
            persona=persona,
            personality=personality,
            scenario=scenario,
            examples_of_dialogue=examples_of_dialogue,
            custom_role_template_type=custom_role_template_type,
            model_id=model_id,
            scene_id = scene_id,
            voice_id=voice_id
        )
        custom_role.save()

        target= reverse('omserver/index')
        return redirect(target, locals())


    @api_view(['POST'])
    def character_role_modify2(request, pk):
        data = request.data  # 获取请求的 JSON 数据
        # 从 JSON 数据中提取字段值
        id = data.get('id')
        role_name = data.get('role_name')
        gender = data.get('gender')
        avatar = data.get('avatar')
        persona = data.get('persona')
        personality = data.get('personality')
        scenario = data.get('scenario')
        examples_of_dialogue = data.get('examples_of_dialogue')
        custom_role_template_type = data.get('custom_role_template_type')
        model_id = data.get('model_id')
        voice_id = data.get('voice_id')
        scene_id = data.get('scene_id')

        # 更新 CharacterRoleModel 实例并保存到数据库
        custom_role = CharacterRoleModel(
            id=id,
            role_name=role_name,
            avatar = avatar,
            gender = gender,
            persona=persona,
            personality=personality,
            scenario=scenario,
            examples_of_dialogue=examples_of_dialogue,
            custom_role_template_type=custom_role_template_type,
            model_id = model_id,
            voice_id = voice_id,
            scene_id = scene_id
        )
        custom_role.save()
        return Response({"response": "Data edit to database", "code": "200"})


    @api_view(['POST'])
    def character_role_delete(request, pk):
        role = get_object_or_404(CharacterRoleModel, pk=pk)
        role.delete()
        return Response({"response": "ok", "code": "200"})



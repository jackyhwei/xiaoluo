from django.shortcuts import render, get_object_or_404
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required

from omserver.model.model import BackgroundImageModel
from omserver.serializers import BackgroundImageSerializer

import json
import logging

logger = logging.getLogger(__name__)

@login_required
def background_list(request):
    """
    Retrieve a list of uploaded background images.
    """
    images = BackgroundImageModel.objects.all()

    bgimg_list = serialize('json', images)

    # bgimg = BackgroundImageSerializer(images, many=True)
    # bgimg_list  = {"background_list": [{"id":1, "original_name": "科达网呈", "image": "bg-3.png"}]}
    # return render(request, "background_list.html", context=bgimg_list)
    logger.debug(bgimg_list)
    # [
    #    {"model": "omserver.backgroundimagemodel", "pk": 1, "fields": {"original_name": "111618501duw.png", "image": "background/111618501duw.png"}}, 
    #    {"model": "omserver.backgroundimagemodel", "pk": 2, "fields": {"original_name": "bg-a.png", "image": "background/bg-a.png"}}
    # ]
    j = json.loads(bgimg_list)
    logger.debug("json: " + json.dumps(j))

    return render(request, "background_list.html", {"background_list": json.dumps(j)})

def get_background_by_id(request):
    """
    Retrieve a list of uploaded background images.
    """
    id = request["id"]
    data = BackgroundImageModel.objects.get(id=id)
    res = model_to_dict(data)

    logger.debug(res)
    # [
    #    {"model": "omserver.backgroundimagemodel", "pk": 1, "fields": {"original_name": "111618501duw.png", "image": "background/111618501duw.png"}}, 
    #    {"model": "omserver.backgroundimagemodel", "pk": 2, "fields": {"original_name": "bg-a.png", "image": "background/bg-a.png"}}
    # ]
    j = json.loads(res)

    logger.debug("json: " + json.dumps(j))

    return render(request, "background_list.html", {"background_list": json.dumps(j)})

@api_view(['POST'])
def delete_background_image(request, pk):
    logger.debug(f"delete background image={pk}")

    # 删除数据
    background_image_model = get_object_or_404(BackgroundImageModel, pk=pk)
    background_image_model.delete()

    # 获取要删除的文件路径
    file_path = os.path.join(
        settings.MEDIA_ROOT, str(background_image_model.image))
    # 删除关联的文件
    if os.path.exists(file_path):
        os.remove(file_path)

    return Response({"response": "ok", "code": "200"})


@api_view(['POST'])
def upload_background_image(request):
    """
    Upload a background image.
    """
    logger.debug(f"uploading background image={request.data}")

    serializer = BackgroundImageSerializer(data=request.data)

    if serializer.is_valid():
        # 获取上传文件对象
        uploaded_file = request.data['image']
        # 获取上传文件的原始文件名
        original_filename = uploaded_file.name
        logger.debug("save background image: original_filename={original_filename}")
        serializer.save(original_name=original_filename)
        return Response({"response": "ok", "code": "200"})
    
    return Response({"response": "no", "code": "500"})


@api_view(['GET'])
def show_background_image(request):
    """
    Retrieve a list of uploaded background images.
    """
    images = BackgroundImageModel.objects.all()
    serializer = BackgroundImageSerializer(images, many=True)
    return Response({"response": serializer.data, "code": "200"})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse, HttpResponse, StreamingHttpResponse

import json
import logging
from ..omengine.translation import translationClient

logger = logging.getLogger(__name__)

@login_required
def translate_settings(request):
    return render(request, "translate_settings.html")

@login_required
def translate_youdao(request):
    return render(request, "translate_youdao.html")

@login_required
def translate_houshan(request):
    return render(request, "translate_huoshan.html")

@login_required
def translate_google(request):
    return render(request, "translate_google.html")

@api_view(['POST'])
def translation(request):
    """
    translation
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        text = data["text"]
        target_language = data["target_language"]
        target_result = translationClient.translation(text=text, target_language=target_language)
        return Response({"response": target_result, "code": "200"})
    except Exception as e:
        logger.error(f"translation error: {e}")
        return HttpResponse(status=500, content="Failed to translation error.")

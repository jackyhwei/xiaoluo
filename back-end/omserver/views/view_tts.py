from django.shortcuts import render
from omserver.model.model_tts import TtsVoiceIdModel
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from io import BytesIO
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, StreamingHttpResponse

from ..omengine.tts import single_tts_driver
from omserver.model.model_tts import TtsVoiceIdModel, TtsVoiceCloneModel
from omserver.serializers import TtsVoiceIdSerializer

import logging
import json
import os

logger = logging.getLogger(__name__)

@api_view(['POST'])
def generate(request):
    """
    Generate audio from text.
    """
    try:
        # print("aaaaaaaaaaaaaaaaaaa")
        data = json.loads(request.body.decode('utf-8'))

        # print("json=", json.dumps(data))

        text = data["text"]
        voice_id = data["voice_id"]
        type = data["type"]

        # print("bbbbbbbbbbbbbbbbbbb")

        # logger.debug("generate tts: type=%s, text=%s, voice_id=%s" %(type, text, voice_id))

        file_name = single_tts_driver.synthesis(type=type, text=text, voice_id=voice_id)
        file_path = os.path.join("tmp", file_name)

        # logger.debug(f"generate tts: filepath={file_path}")

        audio_file = BytesIO()
        with open(file_path, 'rb') as file:
            audio_file.write(file.read())

        # delete_file(file_path)
        # logger.debug(f"delete file :{file_path}")

        audio_file.seek(0)

        # Create the response object.
        response = HttpResponse(content_type='audio/mpeg')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        response.write(audio_file.getvalue())
        return response
    except Exception as e:
        logger.error(f"generate_audio error: {e}")
        return HttpResponse(status=500, content="Failed to generate audio.")


def delete_file(file_path):
    os.remove(file_path)

@api_view(['POST'])
def get_voices(request):
    data = json.loads(request.body.decode('utf-8'))
    type = data["type"]
    return Response({"response": single_tts_driver.get_voices(type=type), "code": "200"})

@api_view(['GET'])
def tts_voiceid_list(request):
    # load tts voiceId list
    voice_id = TtsVoiceIdModel.objects.all()
    serializer = TtsVoiceIdSerializer(voice_id, many=True)
    return Response({"response": serializer.data, "code": "200"})

@api_view(['POST'])
def tts_voiceid_new(request):
    return Response({"response": "OK", "code": 200})

@api_view(['POST'])
def tts_voiceid_delete(request):
    return Response({"response": "OK", "code": 200})

@api_view(['GET'])
def tts_voiceclone_list(request):
    # load tts voiceId list
    voice_id = TtsVoiceCloneModel.objects.all()
    voice_id_list = serialize('json', voice_id)
    # j_voiceId = json.loads(voice_id_list)
    # context = {
    #     "tts_voiceId": json.dumps(j_voiceId),
    # }

    return Response({"response": voice_id_list, "code": 200})

@api_view(['GET'])
def tts_voiceclone_new(request):
    data = {"desc": "voice clone task submitted successfully."}
    return Response({"response": data, "code": 200})

@api_view(['GET'])
def tts_voiceclone_del(request):
    data = {"desc": "voice clone deleted successfully."}
    return Response({"response": data, "code": 200})


@login_required
def tts_live(request):
    # load tts voiceId list
    voice_id = TtsVoiceIdModel.objects.all()
    voice_id_list = serialize('json', voice_id)
    j_voiceId = json.loads(voice_id_list)

    context = {
        "tts_voiceId": json.dumps(j_voiceId),
    }

    return render(request, "tts_live.html", context)

@login_required
def tts_clone(request):
    return render(request, 'tts_clone.html')

@login_required
def tts_file(request):
    return render(request, 'tts_file.html')

@login_required
def tts_settings(request):
    ## edge-tts --list-voices
    # Name: zh-CN-XiaoxiaoNeural  Gender: Female  
    # Name: zh-CN-XiaoyiNeural  Gender: Female  
    # Name: zh-CN-YunjianNeural  Gender: Male  
    # Name: zh-CN-YunxiNeural  Gender: Male  
    # Name: zh-CN-YunxiaNeural  Gender: Male  
    # Name: zh-CN-YunyangNeural  Gender: Male  
    # Name: zh-CN-liaoning-XiaobeiNeural  Gender: Female  
    # Name: zh-CN-shaanxi-XiaoniNeural  Gender: Female  
    # Name: zh-HK-HiuGaaiNeural  Gender: Female  
    # Name: zh-HK-HiuMaanNeural  Gender: Female  
    # Name: zh-HK-WanLungNeural  Gender: Male  
    # Name: zh-TW-HsiaoChenNeural  Gender: Female  
    # Name: zh-TW-HsiaoYuNeural  Gender: Female  
    # Name: zh-TW-YunJheNeural  Gender: Male  

    voice_id = TtsVoiceIdModel.objects.all()
    voice_id_list = serialize('json', voice_id)
    j = json.loads(voice_id_list)

    logger.info(f"tts_voiceid_list: {j}")

    context = {'tts_voiceid_list': json.dumps(j)}  # 将JSON数据转换为字符串

    return render(request, 'tts_settings.html', context)

###########################################
# APIs
###########################################

""" @app_omserver.route('/v1/tts/voiceclone/new', methods=['POST'])
def tts_clone_new():
    data = []
    return RETURN_DATA(data)


@app_omserver.route('/v1/tts/voiceclone/load', methods=['GET'])
def tts_clone_load():
    data = omtts.tts_vc_load_all()
    return RETURN_DATA(data)


@app_omserver.route('/v1/tts/perlist/load', methods=['GET'])
def tts_loadPerList():
    index = request.args.get('index', default=0, type=int)
    res = []
    perList = omtts.om_tts_load_perList()

    list = perList["data"]
    for item in list:
        res.append(item)

    print("tts_loadPerList, item: " + json.dumps(res))

    return json.dumps(res);

@app_omserver.route('/v1/tts/perlist/to_excel')
def ajax_down_per_excel():
    per = omtts.om_tts_load_perList()
    j = json.loads(per)
    per_list = j["per"]

    f = io.BytesIO()

    wb = xlwt.Workbook()
    sh1 = wb.add_sheet('sheet1')
    sh1.write(0, 0, "角色模型(name)")
    sh1.write(0, 1, "性别(gender)")
    sh1.write(0, 2, "语言（lan)")
    sh1.write(0, 3, "接口类型(ctp)")
    sh1.write(0, 4, "音调（pit）")
    sh1.write(0, 5, "语速(spd)")
    sh1.write(0, 6, "am")
    sh1.write(0, 7, "voc")

    sheet_index = 1
    for item in per_list:
        sh1.write(sheet_index, 0, item["name"])
        if item["gender"] == 0:
            sh1.write(sheet_index, 1, "女")
        elif item["gender"] == 1:
            sh1.write(sheet_index, 1, "男")
        else:
            sh1.write(sheet_index, 1, "可咸可甜")
        sh1.write(sheet_index, 2, item["lan"])
        sh1.write(sheet_index, 3, item["ctp"])
        sh1.write(sheet_index, 4, item["pit"])
        sh1.write(sheet_index, 5, item["spd"])
        sh1.write(sheet_index, 6, item["am"])
        sh1.write(sheet_index, 7, item["voc"])
        sheet_index = sheet_index + 1
    wb.save(f)
    f.seek(0)

    # 发送纪要文件
    return send_file(f, as_attachment=True,
                     attachment_filename=f"tts_per.xls") """

'''
接口路径：GET /v1/tts

备注
    需要根据 Content-Type的头部来确定是否服务端合成成功。
    如果合成成功，返回的Content-Type以“audio”开头
    aue =3 ，返回为二进制mp3文件，具体header信息 Content-Type: audio/mp3；
    aue =4 ，返回为二进制pcm文件，具体header信息 Content-Type:audio/basic;codec=pcm;rate=16000;channel=1
    aue =5 ，返回为二进制pcm文件，具体header信息 Content-Type:audio/basic;codec=pcm;rate=8000;channel=1
    aue =6 ，返回为二进制wav文件，具体header信息 Content-Type: audio/wav；
    如果合成出现错误，则会返回json文本，具体header信息为：Content-Type: application/json。其中sn字段主要用于DEBUG追查问题，如果出现问题，可以提供sn帮助确认问题。
    错误示例：
    {"err_no":500,"err_msg":"notsupport.","sn":"abcdefgh","idx":1}

请求参数
Query：
参数名称	是否必须	示例	备注
lan	是	语言
vol	是	音量，基础音库取值0-9，精品音库取值0-15，默认为5中音量（取值为0时为音量最小值，并非为无声）
ctp	是	客户端类型选择，web端填写固定值1
pit	是	音调，取值0-15，默认为5中语调
spd	是	语速，取值0-15，默认为5中语速
per	是	角色，度小宇=1，度小美=0，度逍遥（基础）=3，度丫丫=4, 度逍遥（精品）=5003，度小鹿=5118，度博文=106，度小童=110，度小萌=111，度米朵=103，度小娇=5
aue	是	3为mp3格式(默认)； 4为pcm-16k；5为pcm-8k；6为wav（内容同pcm-16k）; 注意aue=4或者6是语音识别要求的格式，但是音频内容不是语音识别要求的自然人发音，所以识别效果会受影响。
tok	是	开放平台获取到的开发者[access_token]获取 Access Token "access_token")
cuid	是	用户唯一标识，用来计算UV值。建议填写能区分用户的机器 MAC 地址或 IMEI 码，长度为60字符以内

返回数据
名称	类型	是否必须	默认值	备注	其他信息
暂无数据
'''


"""
@app_omserver.route('/v1/tts', methods=['GET'])
def tts():
    per = request.args.get("per")
    vol = request.args.get('vol')
    pit = request.args.get('pit')
    spd = request.args.get('spd')
    text = request.args.get('tex')
    remote_tts_svr = request.args.get('remote_tts_svr')

    logger.debug(f"tts request: input spd={spd}, vol={vol}, per={per}, pit={pit}, remote_tts_svr={remote_tts_svr}, text=\"{text}\"")
    file = omtts.om_tts(text, per, spd, vol, pit, remote_tts_svr)
    logger.debug((f"tts response: output wavfile={file}"))

    return file

@app_omserver.route('/v1/tts/download_audio')
def tts_ajax_download_perlist():
    tts_id = request.args.get("tts_id")
    tts_records = None
    logger.info(f"tts_id:{tts_id}, content:{tts_records}")

    # 发送
    return send_file(f"{tts_records.tts_name}的音频.wav")

 """
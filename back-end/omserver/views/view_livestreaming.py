from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
import json
import logging
import os

from django.urls import reverse

from omserver.model.model import CSysConfigModel
from omserver.config.sys_config import g_config_dir, g_config_path, g_sys_code

# config_dir = os.path.dirname(os.path.abspath(__file__))
# config_path = os.path.join(config_dir, '../config/sys_config.json')
# sys_code = "adminSettings"

logger = logging.getLogger(__name__)

@login_required
def live_settings(request):
    if request.method == "GET":
        return render(request, "live_settings.html")
    else:
        pass

@login_required
def live_bilibili(request):
    if request.method == "GET":
        session_cfg = request.session["cfg"]
        print(f"cfg={session_cfg}")
        j = json.loads(session_cfg)
        context = {
            "enabled": j["liveConnecterConfig"]["cfg"]["bili"]["enabled"],
            "ROOM_UID_BILI": j["liveConnecterConfig"]["cfg"]["bili"]["ROOM_UID_BILI"],
            "ROOM_ID_BILI": j["liveConnecterConfig"]["cfg"]["bili"]["ROOM_ID_BILI"],
            "ROOM_COOKIE_BILI": j["liveConnecterConfig"]["cfg"]["bili"]["ROOM_COOKIE_BILI"]
        }
        return render(request, "livestreaming_bilibili.html", context)
    else:
        # # ajax json POST递交
        # data = json.loads(request.body)
        # ROOM_UID_BILI = data.get('ROOM_UID_BILI', "-")
        # ROOM_ID_BILI = data.get('ROOM_ID_BILI', "-")

        # 表单POST递交
        ROOM_UID_BILI = request.POST.get('ROOM_UID_BILI', "-")
        ROOM_ID_BILI = request.POST.get('ROOM_ID_BILI', "-")
        ROOM_COOKIE_BILI = request.POST.get('ROOM_COOKIE_BILI', "-")
        enabled = request.POST.get('enabled', '0')
        user_id = request.session["user_id"]

        session_cfg = request.session["cfg"]
        j = json.loads(session_cfg)

        # print(f"requset.post={request.POST}")
        # print(f"userid={user_id}, ROOM_UID_BILI={ROOM_UID_BILI}, ROOM_ID_BILI={ROOM_ID_BILI}, ROOM_COOKIE_BILI={ROOM_COOKIE_BILI}")

        # 检查是否已经有sysconfig，并保存到数据库
        default_sys_config_json = "{}"
        db_cfg = CSysConfigModel.objects.filter(code=g_sys_code, user_id=user_id).first()
        if db_cfg == None:
            logger.debug("=> save default sys config to db")
            print("\n\n[sys_config] config_path=%s\n\n" %(g_config_path))

            with open(g_config_path, 'r', encoding='utf-8') as f:
                default_sys_config_json = json.load(f)
                print("\n\nsys_config_json=%s\n\n" %(default_sys_config_json))

            default_sys_config_json["liveConnecterConfig"]["cfg"]["bili"]["ROOM_UID_BILI"] = ROOM_UID_BILI
            default_sys_config_json["liveConnecterConfig"]["cfg"]["bili"]["ROOM_ID_BILI"] = ROOM_ID_BILI
            default_sys_config_json["liveConnecterConfig"]["cfg"]["bili"]["ROOM_COOKIE_BILI"] = ROOM_COOKIE_BILI
            default_sys_config_json["liveConnecterConfig"]["cfg"]["bili"]["enabled"] = enabled
            
            print(f"cfg={json.dumps(default_sys_config_json)}")

            sys_config_model = CSysConfigModel(code=g_sys_code, config=json.dumps(default_sys_config_json), user_id=user_id)
            sys_config_model.save()
        else:
            j["liveConnecterConfig"]["cfg"]["bili"]["ROOM_UID_BILI"] = ROOM_UID_BILI
            j["liveConnecterConfig"]["cfg"]["bili"]["ROOM_ID_BILI"] = ROOM_ID_BILI
            j["liveConnecterConfig"]["cfg"]["bili"]["ROOM_COOKIE_BILI"] = ROOM_COOKIE_BILI
            j["liveConnecterConfig"]["cfg"]["bili"]["enabled"] = enabled
            print(f"cfg={json.dumps(j)}")
            db_cfg.config = json.dumps(j)
            db_cfg.save()
        
        # 更新session
        request.session["cfg"] = json.dumps(j)

        target= reverse('live_bilibili')
        return redirect(target, locals())

@login_required
def live_douyin(request):
    if request.method == "GET":
        session_cfg = request.session["cfg"]
        print(f"cfg={session_cfg}")
        j = json.loads(session_cfg)

        enabled = j.get('liveConnecterConfig').get('cfg').get('douyin').get('enabled')
        if enabled == None:
            enabled = "0"
        else:
            enabled = enabled
        ROOM_ID_DOUYIN = j.get('liveConnecterConfig').get('cfg').get('douyin').get('ROOM_ID_DOUYIN')
        if ROOM_ID_DOUYIN == None:
            ROOM_ID_DOUYIN = "-"

        context = {
            "enabled": enabled,
            "ROOM_ID_DOUYIN": ROOM_ID_DOUYIN,
        }
        return render(request, "livestreaming_douyin.html", context)
    else:
        # 表单POST递交
        ROOM_ID_DOUYIN = request.POST.get('ROOM_ID_DOUYIN', "-")
        enabled = request.POST.get('enabled', '0')
        user_id = request.session["user_id"]

        session_cfg = request.session["cfg"]
        j = json.loads(session_cfg)

        # print(f"requset.post={request.POST}")
        # print(f"userid={user_id}, ROOM_UID_BILI={ROOM_UID_BILI}, ROOM_ID_BILI={ROOM_ID_BILI}, ROOM_COOKIE_BILI={ROOM_COOKIE_BILI}")

        # 检查是否已经有sysconfig，并保存到数据库
        default_sys_config_json = "{}"
        db_cfg = CSysConfigModel.objects.filter(code=g_sys_code, user_id=user_id).first()
        if db_cfg == None:
            logger.debug("=> save default sys config to db")
            print("\n\n[sys_config] config_path=%s\n\n" %(g_config_path))

            with open(g_config_path, 'r', encoding='utf-8') as f:
                default_sys_config_json = json.load(f)
                print("\n\nsys_config_json=%s\n\n" %(default_sys_config_json))

            default_sys_config_json["liveConnecterConfig"]["cfg"]["douyin"]["ROOM_ID_DOUYIN"] = ROOM_ID_DOUYIN
            default_sys_config_json["liveConnecterConfig"]["cfg"]["douyin"]["enabled"] = enabled
            
            print(f"cfg={json.dumps(default_sys_config_json)}")

            sys_config_model = CSysConfigModel(code=g_sys_code, config=json.dumps(default_sys_config_json), user_id=user_id)
            sys_config_model.save()
        else:
            j["liveConnecterConfig"]["cfg"]["douyin"]["ROOM_ID_DOUYIN"] = ROOM_ID_DOUYIN
            j["liveConnecterConfig"]["cfg"]["douyin"]["enabled"] = enabled
            print(f"cfg={json.dumps(j)}")
            db_cfg.config = json.dumps(j)
            db_cfg.save()
        
        # 更新session
        request.session["cfg"] = json.dumps(j)

        target= reverse('live_douyin')
        return redirect(target, locals())


@login_required
def live_taobao(request):
    return render(request, "livestreaming_taobao.html")

@login_required
def live_kuaishou(request):
    return render(request, "livestreaming_kuaishou.html")

@login_required
def live_douyv(request):
    return render(request, "livestreaming_douyv.html")

@login_required
def live_rtmp(request):
    return render(request, "livestreaming_rtmp.html")

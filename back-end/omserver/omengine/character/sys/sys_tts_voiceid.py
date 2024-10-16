# from ..character_tts_voiceid import Character_VoiceID
from ....model.model_tts import TtsVoiceIdModel

import logging 
logger = logging.getLogger(__name__)

def initSysDefaultVoiceId():
    try:
        result = TtsVoiceIdModel.objects.all()
        if len(result) == 0:
            logger.info("=> load default TTS voiceId")
            # per_name = ""
            # per_gender: str
            # per_lan: str
            # per_spd: str
            # per_pit: str
            # per_vol: str
            # per_am: str
            # per_voc: str
            # per_status: str

            # sys_character_voiceid = Character_VoiceID(per_name=per_name, per_gender=per_gender,
            #                         per_lan=per_lan, per_spd=per_spd, per_pit=per_pit,per_vol=per_vol, 
            #                         per_am=per_am, per_voc=per_voc,per_status=per_status)

            data = [
                {"id": 1, "voice_id": 'zh-CN-XiaoxiaoNeural', "voice_name": '普通话-女-xiaoxiao', "voice_gender": "0", "voice_dialect": "mandarin"},
                {"id": 2, "voice_id": 'zh-CN-XiaoyiNeural', "voice_name": '普通话-女-xiaoyi', "voice_gender": "0", "voice_dialect": "mandarin"},
                {"id": 3, "voice_id": 'zh-CN-YunjianNeural', "voice_name": '普通话-男-yunjian', "voice_gender": "1", "voice_dialect": "mandarin"},
                {"id": 4, "voice_id": 'zh-CN-YunxiNeural', "voice_name": '普通话-男-yunxi', "voice_gender": "1", "voice_dialect": "mandarin"},
                {"id": 5, "voice_id": 'zh-CN-YunxiaNeural', "voice_name": '普通话-男-yunxia', "voice_gender": "1", "voice_dialect": "mandarin"},
                {"id": 6, "voice_id": 'zh-CN-YunyangNeural', "voice_name": '普通话-男-yunyang', "voice_gender": "1", "voice_dialect": "mandarin"},
                {"id": 7, "voice_id": 'zh-CN-liaoning-XiaobeiNeural', "voice_name": '东北话-女-xiaobei', "voice_gender": "0", "voice_dialect": "dongbei"},
                {"id": 8, "voice_id": 'zh-CN-shaanxi-XiaoniNeural', "voice_name": '陕西话-女-xiaoni', "voice_gender": "0", "voice_dialect": "shanxi"},
                {"id": 9, "voice_id": 'zh-HK-HiuGaaiNeural', "voice_name": '粤语-女-hiugaai', "voice_gender": "0", "voice_dialect": "cantonese"},
                {"id": 10, "voice_id": 'zh-HK-HiuMaanNeural', "voice_name": '粤语-女-hiumaan', "voice_gender": "0", "voice_dialect": "cantonese"},
                {"id": 11, "voice_id": 'zh-HK-WanLungNeural', "voice_name": '粤语-男-wanlung', "voice_gender": "1", "voice_dialect": "cantonese"},
                {"id": 12, "voice_id": 'zh-TW-HsiaoChenNeural', "voice_name": '台湾话-女-hsiaochen', "voice_gender": "1", "voice_dialect": "taiwanese"},
                {"id": 13, "voice_id": 'zh-TW-HsiaoYuNeural', "voice_name": '台湾话-女-hsioayu', "voice_gender": "0", "voice_dialect": "taiwanese"},
                {"id": 14, "voice_id": 'zh-TW-YunJheNeural', "voice_name": '台湾话-男-yunjhe', "voice_gender": "1", "voice_dialect": "taiwanese"},
            ];

            logger.debug("------------>>>>>>>>>>>initSysDefaultVoiceId<<<<<<<<<<<------------")
            logger.debug(f"data: {data}\n")

            # 将数据转换为模型对象列表
            objects = []
            for item in data:
                obj = TtsVoiceIdModel(**item)
                objects.append(obj)
            
            # 使用bulk_create()函数进行批量创建
            TtsVoiceIdModel.objects.bulk_create(objects)

    except Exception as e:
        logger.exception("=> load TTS voiceId ERROR: %s" % str(e))

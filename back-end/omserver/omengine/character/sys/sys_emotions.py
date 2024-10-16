from ....model.model_character import CharacterEmotionModel

import logging 
logger = logging.getLogger(__name__)

def initSysDefaultEmotion():
    try:
        result = CharacterEmotionModel.objects.all()
        if len(result) == 0:
            logger.info("=> load default character emotions")
            data = [
                {"id":1, "emotion_model": 'neutral', "emotion_name": '正常'},
                {"id":2, "emotion_model": 'blink', "emotion_name": '眨眨眼'},
                {"id":3, "emotion_model": 'happy', "emotion_name": '开心的'},
                {"id":4, "emotion_model": 'angry', "emotion_name": '生气的'},
                {"id":5, "emotion_model": 'sad', "emotion_name": '伤心的'},
                {"id":6, "emotion_model": 'relaxed', "emotion_name": '放松的'},
                {"id":7, "emotion_model": 'surprised', "emotion_name": '惊讶的'},
                {"id":8, "emotion_model": 'lookUp', "emotion_name": '向上看'},
                {"id":9, "emotion_model": 'lookDown', "emotion_name": '向下看'},
                {"id":10, "emotion_model": 'lookLeft', "emotion_name": '向左看'},
                {"id":11, "emotion_model": 'lookRight', "emotion_name": '向右看'},
                {"id":12, "emotion_model": 'blinkLeft', "emotion_name": '眨左眼'},
                {"id":13, "emotion_model": 'blinkRight', "emotion_name": '眨右眼'},
            ]

            logger.debug(f"data: {data}\n")

            # 将数据转换为模型对象列表
            objects = []
            for item in data:
                obj = CharacterEmotionModel(**item)
                objects.append(obj)
            
            # 使用bulk_create()函数进行批量创建
            CharacterEmotionModel.objects.bulk_create(objects)
    except Exception as e:
        logger.exception("=> load character emotions ERROR: %s" % str(e))


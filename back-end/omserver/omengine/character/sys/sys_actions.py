from ....model.model_character import CharacterActionModel

import logging
logger = logging.getLogger(__name__)

def initSysDefaultActions():
    try:
        result = CharacterActionModel.objects.all()
        if len(result) == 0:
            logger.info("=> init system default character actions\n")
            logger.debug("------------>>>>>>>>>>>initSysDefaultActions()<<<<<<<<<<<------------")
            # 定义要创建的数据列表
            data = [
                {"id": 1, "action_model": 'fbx/dance-male-silly-dancing.fbx', "action_name": '跳舞-科目三', "action_gender": "2", "action_avatar":"thumbnail/dance-male-silly-dancing.gif", "memo": "dance: silly dancing"},
                {"id": 2, "action_model": 'fbx/dance-female-rumba-dancing.fbx', "action_name": '跳舞-伦巴', "action_gender": "2", "action_avatar": "thumbnail/dance-female-rumba-dancing.gif", "memo": "dance: female rumba dancing"},
                # 文件太大，默认禁用
                {"id": 3, "action_model": 'fbx/dancing-male-gangnam-style.fbx', "action_name": "跳舞-GangnamStyle", "action_gender": "2", "action_avatar": "thumbnail/dancing-male-gangnam-style.gif", "memo": "dance: 欧巴缸南style", "status": "0"},
                {"id": 4, "action_model": 'fbx/angry-female-standing-angrily.fbx', "action_name": '生气', "action_gender": "0", "action_avatar": "thumbnail/angry-female-standing-angrily.gif", "memo": "angry: female standing angrily"},
                {"id": 5, "action_model": 'fbx/excited-female-super-excited.fbx', "action_name": '兴奋', "action_gender": "0", "action_avatar": "thumbnail/excited-female-super-excited.gif", "memo": "excited: female super excited"},
                {"id": 6, "action_model": 'fbx/greeting-female-standing.fbx', "action_name": '问候（站立）', "action_gender": "0", "action_avatar": "thumbnail/greeting-female-standing.gif", "memo": "greeting: female standing greeting"},
                {"id": 7, "action_model": 'fbx/thinking-female-thinking-while-standing.fbx', "action_name": '思考', "action_gender": "0", "action_avatar": "thumbnail/thinking-female-thinking-while-standing.gif", "memo": "thinking: female thinking while standing"},
                {"id": 8, "action_model": 'fbx/talking-female-general-conversation.fbx', "action_name": 'talking_01', "action_gender": "2", "action_avatar": "thumbnail/talking-female-general-conversation.gif", "memo": "talking: female general conversation"},
                {"id": 9, "action_model": 'fbx/happy-female-standing-happily.fbx', "action_name": 'idle_happy_01', "action_gender": "2", "action_avatar": "thumbnail/happy-female-standing-happily.gif", "memo": "happy: female standing happily"},
                {"id": 10,"action_model": 'fbx/idle-male.fbx', "action_name": 'idle-male', "action_gender": "2", "action_avatar": "thumbnail/idle-male.gif", "memo": "idle: male"},
                {"id": 11,"action_model": 'fbx/idle-female.fbx', "action_name": 'idle-female', "action_gender": "0", "action_avatar": "thumbnail/idle-female.gif", "memo": "idle: female"},
                {"id": 12,"action_model": 'fbx/idle-female2.fbx', "action_name": 'idle-female2', "action_gender": "0", "action_avatar": "thumbnail/idle-female2.gif", "memo": "idle: female2"},
                # 动作与模型不匹配，先禁用
                {"id": 13, "action_model": 'fbx/talking-male-asking-a-question-with-one-hand.fbx', "action_name": '思考2', "action_gender": "1", "action_avatar": "thumbnail/talking-male-asking-a-question-with-one-hand.gif", "memo": "thinking: talking male asking a question with one hand", "status": "0"},
                # 找不到男性的thinking animation，用这个talking的替代
                {"id": 14, "action_model": 'fbx/greeting-male-quick-formal-bow.fbx', "action_name": 'quick-bow', "action_gender": "1", "action_avatar": "thumbnail/greeting-male-quick-formal-bow.gif", "memo": "greeting: male quick formal bow"},
            ]
        
            logger.debug(f"data: {data}\n")

            # 将数据转换为模型对象列表
            objects = []
            for item in data:
                obj = CharacterActionModel(**item)
                objects.append(obj)
            
            # 使用bulk_create()函数进行批量创建
            CharacterActionModel.objects.bulk_create(objects)
    except Exception as e:
        logger.exception("=> load character actions ERROR: %s" % str(e))


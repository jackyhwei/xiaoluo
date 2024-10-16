from ....model.model_character import CharacterModelModel

import logging
logger = logging.getLogger(__name__)

def initSysDefault3dModels():
  try:
    result = CharacterModelModel.objects.all()
    if len(result) == 0:
      logger.info("=> load default character vrm model")
      data = [
        { "vrm_id": "sys_01", "vrm_type": "system", "vrm_gender": "0", "vrm_name": "[二次元] 海蕾", "vrm_url": "model/hailey.vrm" },
        { "vrm_id": "sys_02", "vrm_type": "system", "vrm_gender": "0", "vrm_name": "[二次元] 活力少女", "vrm_url": "model/活力少女.vrm" },
        { "vrm_id": "sys_03", "vrm_type": "system", "vrm_gender": "1", "vrm_name": "[商务] 印度男", "vrm_url": "model/male_indian.vrm" },
        { "vrm_id": "sys_04", "vrm_type": "system", "vrm_gender": "1", "vrm_name": "[休闲] Joe", "vrm_url": "model/character-joe.vrm" },
        { "vrm_id": "sys_05", "vrm_type": "system", "vrm_gender": "0", "vrm_name": "[商务] 印度女", "vrm_url": "model/female-indian-office-woman.vrm" },
        { "vrm_id": "sys_06", "vrm_type": "system", "vrm_gender": "0", "vrm_name": "[商务] 印度女学生", "vrm_url": "model/female-indian-teenage-woman.vrm" },
        { "vrm_id": "sys_07", "vrm_type": "system", "vrm_gender": "0", "vrm_name": "[游戏] 弥豆子", "vrm_url": "model/game.nezuko.kamado.vrm" },
        { "vrm_id": "sys_08", "vrm_type": "system", "vrm_gender": "0", "vrm_name": "[游戏] 伊邪那美", "vrm_url": "model/xiaomei.vrm" }
      ]

      logger.debug("------------>>>>>>>>>>>initSysDefault3dModels<<<<<<<<<<<------------")
      logger.debug(f"data: {data}\n")

      # 将数据转换为模型对象列表
      objects = []
      for item in data:
        obj = CharacterModelModel(**item)
        objects.append(obj)

      # 使用bulk_create()函数进行批量创建
      CharacterModelModel.objects.bulk_create(objects)

  except Exception as e:
    logger.exception("=> load character vrm models ERROR: %s" % str(e))


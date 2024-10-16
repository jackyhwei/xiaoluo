from django.db import models

class CharacterRoleModel(models.Model):
  '''统一自定义角色定义数据结构
  role_name: 角色名称
  gender: 性别
  persona: 角色基本信息定义
  personality: 角色的性格简短描述
  scenario: 角色的对话的情况和背景
  examples_of_dialogue: 角色的对话样例
  '''
  id = models.AutoField
  role_name = models.CharField(max_length=100)
  avatar = models.CharField(max_length=250, null=True, blank=True, default="")
  gender = models.SmallIntegerField(default=2)
  persona = models.TextField()
  personality = models.TextField()
  scenario = models.TextField()
  examples_of_dialogue = models.TextField()
  custom_role_template_type = models.CharField(max_length=50)
  model_id = models.CharField(max_length=250, null=True, blank=True, default="")
  scene_id = models.CharField(max_length=250, null=True, blank=True, default="")
  voice_id = models.CharField(max_length=32, null=True, blank=True, default="")
  user_id  = models.CharField(max_length=32, null=True, blank=True, default="")
  permission = models.SmallIntegerField(default=0, null=True, blank=True)
  
  def __str__(self):
      return self.role_name

class CharacterRoleTemplateModel(models.Model):
  '''虚拟人角色模板模块
  '''
  id = models.AutoField
  role_template_name = models.CharField(max_length=100)
  gender = models.SmallIntegerField(default=2)
  persona = models.TextField()
  personality = models.TextField()
  scenario = models.TextField()
  examples_of_dialogue = models.TextField()
  custom_role_template_type = models.CharField(max_length=50)

  def __str__(self):
      return self.role_template_name

class CharacterModelModel(models.Model):
  '''3D人物模型模块
  '''
  id = models.AutoField
  vrm_id = models.CharField(max_length=32)
  vrm_avatar = models.FileField(upload_to='thumbnail/', null=True, blank=True)
  vrm_type = models.CharField(max_length=64)
  vrm_gender = models.SmallIntegerField(default=2)
  vrm_name = models.CharField(max_length=128)
  vrm_url = models.FileField(upload_to='model/')
  status = models.SmallIntegerField(default=1)
  vrm_memo = models.CharField(max_length=1024, null=True, blank=True)
  user_id = models.IntegerField(default=0, null=True, blank=True)
  permission = models.IntegerField(default=0, null=True, blank=True)

  def __str__(self):
      return self.vrm_name

class CharacterEmotionModel(models.Model):
  '''3D人物表情
  '''
  id = models.AutoField
  emotion_name = models.CharField(max_length=64)
  emotion_model = models.CharField(max_length=250)     # FBX文件路径
  status = models.SmallIntegerField(default=1) 
  memo = models.CharField(max_length=256)

class CharacterActionModel(models.Model):
  '''3D人物动作
  '''
  id = models.AutoField
  action_name = models.CharField(max_length=64)
  action_avatar = models.FileField(upload_to='thumbnail/', null=True, blank=True)
  action_type = models.CharField(max_length=64, null=True, blank=True)
  action_gender = models.SmallIntegerField(default=2)
  action_model = models.FileField(upload_to='fbx/', null=True, blank=True)     # FBX文件路径
  status = models.SmallIntegerField(default=1)
  memo = models.CharField(max_length=256)
  user_id = models.IntegerField(default=0, null=True, blank=True)
  permission = models.IntegerField(default=0, null=True, blank=True)

  def __str__(self):
      return self.action_name

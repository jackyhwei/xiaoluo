from datetime import datetime 
from django.db import models

class LlmLocalMemoryModel(models.Model):
  '''记忆数据存储数据结构
  id: 主键ID
  text: 记忆文本
  sender: 发送者
  owner: 记忆的所有人
  timestamp: 创建时间

  chat_id: GUID for chat
  role_id: CharacterRoleModel.id
  user_id: AuthUser.id
  emotion: reserved
  kb_id: LLmKnowledgeBaseModel
  llm_type: llm type
  user_ip: user ip addr
  '''
  id = models.AutoField

  text = models.TextField()
  tags = models.TextField()
  owner = models.CharField(max_length=50)
  sender = models.CharField(max_length=50,default="null")
  timestamp = models.DateTimeField(null=True, blank=True, default=datetime.now, verbose_name="create time")

  chat_id = models.CharField(max_length=64,default="null")
  role_id = models.IntegerField(default=1)
  user_id = models.IntegerField(default=1)
  emotion = models.CharField(max_length=32,default="null")
  kb_id = models.CharField(max_length=64, default="null")
  llm_type = models.CharField(max_length=64, default="null")
  user_ip = models.CharField(max_length=64, default="null")
  # importance = models.SmallIntegerField(default=0)

  def __str__(self):
      return self.id
  
class LLmKnowledgeBaseModel(models.Model):
  id = models.AutoField
  kb_id = models.CharField(max_length=64)
  kb_name = models.CharField(max_length=64)
  kb_path = models.CharField(max_length=2048)
  kb_owner_id = models.IntegerField()
  kb_memo = models.CharField(max_length=1024)
  user_id = models.IntegerField(default=0, null=True, blank=True)

class LlmPromptModel(models.Model):
  id = models.AutoField
  prompt_type = models.CharField(max_length=32)
  prompt_name = models.CharField(max_length=128)
  prompt_language = models.CharField(max_length=32, null=True, blank=True, default="zh")
  prompt_personality = models.CharField(max_length=260, null=True, blank=True)
  prompt_scenario = models.CharField(max_length=260, null=True, blank=True)
  prompt_content = models.TextField()


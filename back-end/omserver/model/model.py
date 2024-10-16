from django.db import models
from django.contrib.auth.models import AbstractUser

class CSysConfigModel(models.Model):
  '''系统配置数据结构
  id: 主键id
  code: 配置code
  config: 配置json
  '''
  id = models.AutoField
  user_id = models.IntegerField(default=0, null=True, blank=True)
  code = models.CharField(max_length=20)
  config = models.TextField()

  def __str__(self):
      return self.id
 
# class CustomUser(AbstractUser):
#   username = models.CharField(max_length=150) # non-unique
#   email = models.CharField(max_length=150, unique=True) # non-unique
#   phone_number = models.CharField(max_length=15, blank=True)
#   birthdate = models.DateField(null=True, blank=True)  # 可选字段，可以为空
#   authcode = models.CharField(max_length=32, blank=True, default="OddMeta")

class BackgroundImageModel(models.Model):
  id = models.AutoField
  original_name = models.CharField(max_length=50)
  image = models.ImageField(upload_to='background/')
  user_id = models.IntegerField(default=0, null=True, blank=True)

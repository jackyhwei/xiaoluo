from django.db import models

class AsrHotwordsModel(models.Model):
    ###############################################
    ## ASR 热词表：
    #       hotwords_type   1：人名，2：地名，3：专有名词
    ###############################################
    id = models.AutoField
    hotwords_id = models.CharField(max_length=64)
    hotwords_type = models.CharField(max_length=32)
    words = models.TextField()
    def __str__(self):
        return self.id

class AsrSensitivewordsModel(models.Model):
    ###############################################
    ## ASR 敏感词表：
    ###############################################
    id = models.AutoField
    unique_id = models.CharField(max_length=64)
    sensitive_word = models.TextField

class AsrRecordsModel(models.Model):
    ###############################################
    ## ASR 转写记录表
    ###############################################
    asr_id = models.AutoField
    asr_name = models.CharField(max_length=1024)
    asr_audio_url = models.CharField(max_length=250)
    asr_text = models.CharField(max_length=1024)

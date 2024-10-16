from django.db import models

class TtsVoiceIdModel(models.Model):
  ###############################################
  ## TTS 预设人物语音
  ###############################################
  id = models.AutoField
  voice_id = models.CharField(max_length=32)
  voice_name = models.CharField(max_length=64)
  voice_gender = models.IntegerField()
  voice_dialect = models.CharField(max_length=32)
  voice_spd = models.IntegerField(null=True, blank=True, default=5)
  voice_pit = models.IntegerField(null=True, blank=True, default=5)
  voice_vol = models.IntegerField(null=True, blank=True, default=5)
  voice_am = models.TextField(null=True, blank=True)
  voice_voc = models.TextField(null=True, blank=True)
  voice_status = models.IntegerField(null=True, blank=True, default=1)

  def __str__(self):
      return self.voice_id

class TtsVoiceCloneModel(models.Model):
  ###############################################
  ## TTS 语音克隆
  ###############################################
  id = models.AutoField
  vc_id = models.CharField(max_length=32)
  vc_name = models.CharField(max_length=64)
  vc_gender = models.IntegerField()
  vc_dialect = models.CharField(max_length=32)
  vc_am = models.CharField(max_length=64, null=True, blank=True, default="")
  vc_am_config = models.TextField(null=True, blank=True, default="")
  vc_voc = models.CharField(max_length=64, null=True, blank=True, default="")
  vc_voc_config = models.TextField(null=True, blank=True, default="")
  vc_wavfiles = models.CharField(max_length=250, null=True, blank=True, default="")
  vc_status = models.IntegerField(null=True, blank=True, default=1)


class TtsRecordsModel(models.Model):
  ###############################################
  ## TTS 语音合成记录
  ###############################################
   tts_id = models.AutoField
   tts_session_id = models.CharField(max_length=64)
   tts_type = models.IntegerField
   tts_name = models.CharField(max_length=1024)
   tts_lan = models.CharField(max_length=32)
   tts_begin_time = models.DateTimeField
   tts_end_time = models.DateTimeField
   tts_text = models.TextField
   tts_audio_url = models.CharField(max_length=250)
   tts_am = models.TextField
   tts_voc = models.TextField
   tts_per = models.IntegerField
   tts_spd = models.IntegerField
   tts_pit = models.IntegerField
   tts_vol = models.IntegerField
   tts_status = models.IntegerField

from datetime import datetime
from django.db import models
from django.utils import timezone

class SchedulesModel(models.Model):
  OM_REPEAT_CHOICES = [
      ('no', '不循环'),
      ('daily', '每日'),
      ('weekly', '每周'),
      ('monthly', '每月'),
      ('yearly', '每年'),
  ]

  OM_WEEKDAY_CHOICES = [
      ('Monday', '周一'),
      ('Tuesday', '周二'),
      ('Wednesday', '周三'),
      ('Thursday', '周四'),
      ('Friday', '周五'),
      ('Saturday', '周六'),
      ('Sunday', '周日'),
  ]

  id = models.AutoField

  title = models.CharField(max_length=255, verbose_name="会议标题")

  location = models.CharField(null=True, blank=True, max_length=255, verbose_name="会议地点")
  description = models.TextField(null=True, blank=True, verbose_name="会议描述")
  # created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='created_meetings', verbose_name="创建者")
  created_by = models.IntegerField(null=True, blank=True, default=1, verbose_name="创建者")
  created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True, verbose_name="创建时间")
  updated_at = models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name="更新时间")

  # start_time = models.DateTimeField(verbose_name="开始时间")
  start_time = models.CharField(max_length=32, verbose_name="开始时间")

  # end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
  end_time = models.CharField(null=True, blank=True, max_length=32, verbose_name="结束时间")

  recurring_type = models.CharField(blank=True, max_length=10, choices=OM_REPEAT_CHOICES, verbose_name="重复类型")
  repeat_day_of_week = models.CharField(null=True, blank=True, max_length=9, choices=OM_WEEKDAY_CHOICES, verbose_name="重复周几")

  # 关于repeat_month_day取值
  # 1）不循环：完整的年月日时间。如：2024-05-16，代表2024年5月16日单次任务，不循环。
  # 2）daily: 置空。
  # 3）weekly: 置空。
  # 4）monthly: 日期。如：10，代表每月10号循环任务。
  # 5）yearly: 月日。如：12-10，代表每年12月10日循环任务。
  repeat_month_day = models.CharField(null=True, blank=True, max_length=9, verbose_name="重复月日")
  repeat_end_date = models.DateTimeField(null=True, blank=True, verbose_name="重复结束日期")

  attendees = models.CharField(max_length=256, null=True, blank=True)

  tool = models.CharField(max_length=32, null=True, blank=True)
  user_id = models.IntegerField(default=1, null=True)
  status = models.SmallIntegerField(null=True, blank=True, default=0)
  original_input = models.CharField(null=True, blank=True, max_length=512)

  class Meta:
      verbose_name = "会议日程"
      verbose_name_plural = "会议日程"

  def __str__(self):
      return f"{self.title} - {self.start_time}"

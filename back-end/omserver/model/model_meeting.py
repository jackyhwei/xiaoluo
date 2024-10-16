from django.db import models
from django.utils import timezone

# 循环规则目前只支持每日，每周几，每月几号，每年几月几号
# 对于更复杂的重复规则（例如，每两周一次，或者每月的第二个星期五），
# 可能需要扩展Schedule表的结构，或者设计额外的表来存储这些细节。
# 但基于上述基础设计，可以覆盖大部分常见场景。

class Meeting_Meeting(models.Model):
    title = models.CharField(max_length=255, verbose_name="会议标题")
    location = models.CharField(max_length=255, blank=True, verbose_name="会议地点")
    description = models.TextField(blank=True, verbose_name="会议描述")
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE, 
        related_name='created_meetings', 
        verbose_name="创建者"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "会议"
        verbose_name_plural = "会议"

    def __str__(self):
        return self.title

class Meeting_Schedule(models.Model):
    MEETING_REPEAT_CHOICES = [
        ('daily', '每日'),
        ('weekly', '每周'),
        ('monthly', '每月'),
        ('yearly', '每年'),
    ]
    WEEKDAY_CHOICES = [
        ('Monday', '周一'),
        ('Tuesday', '周二'),
        ('Wednesday', '周三'),
        ('Thursday', '周四'),
        ('Friday', '周五'),
        ('Saturday', '周六'),
        ('Sunday', '周日'),
    ]

    meeting = models.ForeignKey(Meeting_Meeting, on_delete=models.CASCADE, related_name='schedules', verbose_name="会议")
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(verbose_name="结束时间")
    is_recurring = models.BooleanField(default=False, verbose_name="是否重复")
    recurring_type = models.CharField(max_length=10, choices=MEETING_REPEAT_CHOICES, blank=True, verbose_name="重复类型")
    repeat_day_of_week = models.CharField(max_length=9, choices=WEEKDAY_CHOICES, blank=True, verbose_name="重复周几")
    repeat_month_day = models.IntegerField(null=True, blank=True, verbose_name="重复月日")
    repeat_end_date = models.DateTimeField(null=True, blank=True, verbose_name="重复结束日期")

    class Meta:
        verbose_name = "会议日程"
        verbose_name_plural = "会议日程"

    def __str__(self):
        return f"{self.meeting.title} - {self.start_time}"

class Meeting_Attendee(models.Model):
    STATUS_CHOICES = [
        ('invited', '已邀请'),
        ('confirmed', '已确认'),
        ('declined', '已拒绝'),
    ]

    schedule = models.ForeignKey(Meeting_Schedule, on_delete=models.CASCADE, related_name='attendees', verbose_name="日程")
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="参会人")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='invited', verbose_name="参会状态")

    class Meta:
        verbose_name = "参会人"
        verbose_name_plural = "参会人"

    def __str__(self):
        return f"{self.user.username} - {self.schedule.meeting.title}"
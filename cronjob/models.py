from django.db import models
from django.core.exceptions import ValidationError

"""
需求：
1. 一张表记录当前任务
2. 一张表记录任务运行记录

使用django-apscheduler:
django-apscheduer会生成两张表（django_apscheduler_djangojob、django_apscheduler_djangojobexecution）
一个是记录当前任务 一个是记录历史任务 当任务结束时会把历史记录清除掉 不符合我们需求

使用原生apscheduler:
在apscheduler模块中，通常只会创建一个名为apscheduler_jobs的表，该表用于存储调度任务的信息，包括任务的ID、下次执行时间、上次执行时间等等。并不会默认创建历史记录表。
所以需要手动创建一个用于存储历史记录的表，当添加任务后, 将任务信息加入该表中 更新、删除任务都会更新此表
"""


class JenkinsJobExecution(models.Model):
    id = models.BigAutoField(primary_key=True)
    status = models.CharField(max_length=50, verbose_name="任务状态")
    TRIGGER_CHOICES = (
        ('date', 'Date'),
        ('interval', 'Interval'),
        ('cron', 'Cron'),
    )
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES, verbose_name="触发状态")
    run_time = models.CharField(verbose_name="运行时间", max_length=1000)
    duration = models.DurationField(verbose_name="任务耗时(微秒)", null=True)
    finished = models.BooleanField(verbose_name="任务完成", default=False)
    exception = models.CharField(verbose_name="出错信息", max_length=1000, null=True)
    traceback = models.TextField(verbose_name="回溯深度", null=True)
    parameter = models.TextField(verbose_name="任务参数", null=True)
    returned = models.TextField(verbose_name="返回值", null=True)
    job_id = models.CharField(verbose_name="任务ID", max_length=255, unique=True)
    job_name = models.CharField(verbose_name="任务名称", max_length=255)
    job_status = models.CharField(verbose_name="任务状态", max_length=255, null=True)

    class Meta:
        db_table = 'jenkins_apscheduler_jobexecution'

    def clean(self):
        # 验证 trigger 字段的值是否是预定义选项之一
        if self.trigger not in dict(self.TRIGGER_CHOICES):
            raise ValidationError('Invalid trigger value. Allowed values are: date, interval, cron.')
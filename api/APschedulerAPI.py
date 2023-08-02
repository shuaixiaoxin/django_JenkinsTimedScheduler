import os
import secrets
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_JenkinsTimedScheduler.settings')
# import django
# django.setup()

from datetime import datetime
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ADDED, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED, EVENT_JOB_REMOVED, EVENT_SCHEDULER_START, EVENT_SCHEDULER_PAUSED, EVENT_SCHEDULER_RESUMED
from cronjob.models import JenkinsJobExecution
from django_JenkinsTimedScheduler import settings


class ApschedulerAPI:

    def __init__(self):
        job_defaults = {
            'coalesce': False,
            'max_instances': 2
        }

        self.scheduler = BackgroundScheduler(timezone='Asia/Shanghai', job_defaults=job_defaults)
        jobstore = SQLAlchemyJobStore(url=settings.APSCHEDULER_DB)
        self.scheduler.add_jobstore(jobstore, 'default')

        self.scheduler.add_listener(self.job_added_listener, EVENT_JOB_ADDED)
        self.scheduler.add_listener(self.job_started_listener, EVENT_SCHEDULER_START)
        self.scheduler.add_listener(self.job_pause_listener, EVENT_SCHEDULER_PAUSED)
        self.scheduler.add_listener(self.job_resume_listener, EVENT_SCHEDULER_RESUMED)
        self.scheduler.add_listener(self.job_executed_listener, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self.job_error_listener, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self.job_missed_listener, EVENT_JOB_MISSED)
        self.scheduler.add_listener(self.job_removed_listener, EVENT_JOB_REMOVED)
        self.scheduler.start()

    # 任务添加监听
    def job_added_listener(self, event):
        job = self.get_jobs(job_id=event.job_id)
        if job:
            job_id = job[0]
            job_name = job[1]
            job_parameter = [job[2][1:], job[3]]
            job_run_time = job[4]
            trigger = job_id.split('-')[0]
            JenkinsJobExecution.objects.create(status='await', trigger=trigger, run_time=job_run_time, job_id=job_id, job_name=job_name, parameter=job_parameter)

    # 任务启动监听
    def job_started_listener(self, event):
        pass

    # 任务暂停监听
    def job_pause_listener(self, event):
        pass

    # 任务恢复监听
    def job_resume_listener(self, event):
        pass

    # 任务执行监听
    def job_executed_listener(self, event):
        start_time = event.scheduled_run_time
        end_time = datetime.now(start_time.tzinfo)
        execution_time = end_time - start_time
        JenkinsJobExecution.objects.filter(job_id=event.job_id).update(status="executed", duration=execution_time, finished=True, returned=event.retval)

    # 任务错误监听po
    def job_error_listener(self, event):
        start_time = event.scheduled_run_time
        end_time = datetime.now(start_time.tzinfo)
        execution_time = end_time - start_time
        JenkinsJobExecution.objects.filter(job_id=event.job_id).update(status='error', duration=execution_time, finished=True, exception=event.exception)

    # 任务错过监听
    def job_missed_listener(self, event):
        scheduled_time = event.scheduled_run_time
        current_time = datetime.now(scheduled_time.tzinfo)
        missed_duration = current_time - scheduled_time
        JenkinsJobExecution.objects.filter(job_id=event.job_id).update(status='missed', exception=f"在预定时间 {scheduled_time} 上已经错过触发，已经过去了 {missed_duration}.")

    # 任务删除监听
    def job_removed_listener(self, event):
        pass

    # 单次定时
    def date_task(self, func, executionTime, *args, name=None, **kwargs):
        random_hex = 'date-' + str(secrets.token_hex(32))
        self.scheduler.add_job(func, DateTrigger(run_date=executionTime), id=random_hex, name=name, args=args, kwargs=kwargs, replace_existing=True)
        return random_hex

    # 循环定时
    def cron_task(self, func, executionTime, *args, name=None, **kwargs):
        random_hex = 'cron-' + str(secrets.token_hex(32))
        self.scheduler.add_job(func, CronTrigger(**executionTime), id=random_hex, name=name, args=args, kwargs=kwargs, replace_existing=True)
        return random_hex

    # 获取任务信息
    def get_jobs(self, job_id=None, timeCycle=True):
        if job_id:
            job = self.scheduler.get_job(job_id=job_id)
            if job:
                trigger = job.trigger
                if str(trigger).startswith('date'):
                    if timeCycle:
                        run_date = job.trigger.run_date.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        run_date = job.trigger.run_date
                else:
                    run_date = job.trigger
                return job.id, job.name, job.args, job.kwargs, run_date
            else:
                return None
        else:
            all_jobs = self.scheduler.get_jobs()
            if all_jobs:
                jobList = []
                for job in all_jobs:
                    jobDict = {}
                    trigger = job.trigger
                    if str(trigger).startswith('date'):
                        if timeCycle:
                            run_date = job.trigger.run_date.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            run_date = job.trigger.run_date
                    else:
                        run_date = job.trigger
                    jobDict['jobId'] = job.id
                    jobDict['jobName'] = job.name
                    jobDict['jobArgs'] = job.args
                    jobDict['jobKwargs'] = job.kwargs
                    jobDict['next_run_time'] = job.next_run_time
                    jobDict['jobDate'] = run_date
                    jobList.append(jobDict)
                return jobList
            else:
                return None

    def job_pause(self, jobId):
        self.scheduler.pause_job(job_id=jobId)

    def job_resume(self, jobId):
        self.scheduler.resume_job(job_id=jobId)

    def job_remove(self, jobId):
        self.scheduler.remove_job(job_id=jobId)

    def shutdown_scheduler(self):
        self.scheduler.shutdown()


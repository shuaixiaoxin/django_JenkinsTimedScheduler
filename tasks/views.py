import json

from datetime import datetime

from django.core.paginator import Paginator

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer

from cronjob.models import JenkinsJobExecution
from user.response import CustomResponse
from cronjob.views import AP


class JenkinsTaskListView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = 200
        self.message = 'OK'
        self.data = None

    def tasksListPage(self, request):
        return CustomResponse(code=self.code, message=self.message, template_name='cron/task-list.html')

    def taskListAPI(self, request):
        try:
            jobList = []
            jobs = AP.get_jobs()
            if jobs:
                for job in jobs:
                    jobDict = {}
                    jobId = job.get("jobId")

                    task = JenkinsJobExecution.objects.get(job_id=jobId).job_status
                    job_status = '暂停中' if task == 'pause' else '运行中'
                    job_type = '单次定时' if jobId.split('-')[0] == 'date' else '循环定时' if jobId.split('-')[0] == 'cron' else '未知类型'

                    jobDict["jobStatus"] = job_status
                    jobDict["jobType"] = job_type
                    next_time = job.get("next_run_time")
                    if next_time:
                        dt_object = datetime.fromisoformat(str(job.get("next_run_time")))
                        timestamp = dt_object.timestamp()
                        jobDict["next_run_time"] = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                        jobDict["countDown"] = int(timestamp) * 1000
                    else:
                        jobDict["next_run_time"] = '任务已被暂停'
                        jobDict["countDown"] = 1
                        jobDict["jobStatus"] = '暂停中'

                    jobDict["taskId"] = jobId
                    jobDict["jobName"] = job.get("jobName")
                    jobList.append(jobDict)

                self.data = jobList

        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message, data=self.data)

    def paused_task(self, request):
        try:
            data = eval(request.data.get('data'))[0]
            taskId = data.get('taskId')
            jobName = data.get('jobName')
            AP.job_pause(jobId=taskId)
            self.message = f'{jobName}任务已暂停'
        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message, data=self.data)

    def resumed_task(self, request):
        try:
            data = eval(request.data.get('data'))[0]
            taskId = data.get('taskId')
            jobName = data.get('jobName')
            AP.job_resume(jobId=taskId)
            self.message = f'{jobName}任务已恢复'
        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message, data=self.message)

    def remove_task(self, request):
        try:
            # data = eval(request.query_params.get('data'))[0]
            data = eval(request.data.get('data'))[0]
            taskId = data.get('taskId')
            jobName = data.get('jobName')
            AP.job_remove(jobId=taskId)
            self.message = f'{jobName}任务已删除'
        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message, data=self.data)


class JenkinsTaskHistoryView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = 200
        self.message = 'OK'
        self.data = None
        self.DataCount = None

    def tasksHistoryPage(self, request):
        return CustomResponse(code=self.code, message=self.message, template_name='cron/task-history.html')

    def historyListAPI(self, request):
        try:
            pageIndex = request.query_params.get("pageIndex")
            pageSize = request.query_params.get("pageSize")
            taskType = request.query_params.get("taskType")
            taskStatus = request.query_params.get("taskStatus")

            if taskType and taskStatus:
                jobData = JenkinsJobExecution.objects.filter(trigger=taskType, status=taskStatus).values()
            elif taskType:
                jobData = JenkinsJobExecution.objects.filter(trigger=taskType).values()
            elif taskStatus:
                jobData = JenkinsJobExecution.objects.filter(status=taskStatus).values()
            else:
                jobData = JenkinsJobExecution.objects.values()

            self.DataCount = jobData.count()
            jobList = [
                {
                    'taskId': job.get('job_id'),
                    'runTime': job.get('run_time'),
                    'jobName': job.get('job_name'),
                    'jobType': job.get('trigger'),
                    'jobStatus': job.get('status'),
                    'finished': str(job.get('finished')),
                    'duration': job.get('duration'),
                    'jobParameter': job.get('parameter'),
                    'exception': job.get('exception')
                }
                for job in jobData
            ]

            pageInator = Paginator(jobList, pageSize)
            context = pageInator.page(pageIndex)
            self.data = [item for item in context]
        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message, data=self.data, DataCount=self.DataCount)

    def deleteHistory(self, request):
        try:
            if request.user.is_authenticated and request.user.is_superuser:
                jobData = json.loads(request.data.get('data'))
                for job in jobData:
                    taskId = job.get('taskId')
                    if taskId:
                        JenkinsJobExecution.objects.filter(job_id=taskId).delete()
                self.message = '任务删除完成'
            else:
                self.code = 401
                self.message = '当前用户不具有删除任务权限'
        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message)

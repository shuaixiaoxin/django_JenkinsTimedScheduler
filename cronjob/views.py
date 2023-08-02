from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from cron_descriptor import ExpressionDescriptor, Options

# from .signals import custom_signal
from user.response import CustomResponse
from jenkinsConfig.models import UserToken
from api.jenkinsAPI import JenkinsApi
from api.APschedulerAPI import ApschedulerAPI
AP = ApschedulerAPI()


# 单次定时
class JenkinsCronOneView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = 200
        self.message = 'OK'
        self.data = None

    def cron_one_page(self, request):
        try:
            user = request.user
            viewDict = {}
            user_token = UserToken.objects.get(user=user)
            jk = JenkinsApi(str(user), str(user_token))
            views = jk.getView()
            if views[0] == 0:
                for i in views[1]:
                    viewDict[i['name']] = i.get('name')
                self.data = viewDict
            else:
                self.code, self.message = 400, '获取视图组失败'
            return CustomResponse(code=self.code, message=self.message, data=self.data, template_name='cron/cron-one.html')
        except Exception as e:
            return CustomResponse(code=400, message=str(e))

    def viewGroupAPI(self, request):
        try:
            jobsList = []
            data = request.data
            user = request.user
            user_token = UserToken.objects.get(user=user)
            jk = JenkinsApi(str(user), str(user_token))
            viewGroup = data.get('viewGroup')
            if viewGroup:
                if viewGroup == 'all':
                    jobs = jk.getJobs()
                else:
                    jobs = jk.getViewName(viewGroup)
                if jobs[0] == 0:
                    for i in jobs[1]:
                        viewDict = {}
                        viewDict["label"] = i.get('name')
                        viewDict["value"] = i.get('name')
                        jobsList.append(viewDict)
                else:
                    self.code, self.message = 400, '获取任务列表失败'
            self.data = jobsList
        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message, data=self.data)

    def TimedExecution(self, request):
        try:
            user = request.user
            user_token = UserToken.objects.get(user=user)
            jk = JenkinsApi(str(user), str(user_token))
            data = request.data
            view = data.get('view')
            task = data.get('task')
            executionTime = data.get('executionTime')
            res = AP.date_task(jk.buildJob, executionTime, task, name=task)
            self.message = f"{task} 已加入定时任务."
        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message)


# 解析cron表达式 [秒 分 时 日 月 周 年]
def treatmentTime(cron):
    CronTrigger = {}

    try:
        if '?' in cron:
            crontab = cron.replace('?', '*').split()
        else:
            crontab = cron.split()

        cronNum = len(crontab)

        if cronNum == 6 or cronNum == 7:
            keys = ['second', 'minute', 'hour', 'day', 'month', 'day_of_week']
            for i in range(min(cronNum, 6)):
                if keys[i] == 'day_of_week':
                    if isinstance(crontab[i], (int,)):
                        CronTrigger[keys[i]] = int(crontab[i]) - 1
                    elif ',' in crontab[i]:
                        CronTrigger[keys[i]] = ','.join(str(int(x) - 1) for x in crontab[i].split(','))
                    elif '/' in crontab[i]:
                        divider_index = crontab[i].index("/")
                        numerator = crontab[i][:divider_index]
                        denominator = int(crontab[i][divider_index + 1:]) - 1
                        CronTrigger[keys[i]] = f"{numerator}/{denominator}"
                    else:
                        CronTrigger[keys[i]] = crontab[i]
                else:
                    CronTrigger[keys[i]] = crontab[i]
            if cronNum == 7:
                CronTrigger['year'] = crontab[6]
        else:
            raise ValueError("cron表达式格式有误")
    except Exception as e:
        # print("发生错误:", e)
        return None
    return CronTrigger


# 循环定时
class JenkinsCronCycleView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = 200
        self.message = 'OK'
        self.data = None

    def cron_cycle_page(self, request):
        try:
            user = request.user
            viewDict = {}
            user_token = UserToken.objects.get(user=user)
            jk = JenkinsApi(str(user), str(user_token))
            views = jk.getView()
            if views[0] == 0:
                for i in views[1]:
                    viewDict[i['name']] = i.get('name')
            else:
                self.code, self.message = 400, '获取视图组失败'
            self.data = viewDict
            return CustomResponse(code=self.code, message=self.message, data=self.data, template_name='cron/cron-cycle.html')
        except Exception as e:
            return CustomResponse(code=400, message=str(e))

    def CycleTimedExecution(self, request):
        try:
            user = request.user
            user_token = UserToken.objects.get(user=user)
            jk = JenkinsApi(str(user), str(user_token))
            data = request.data
            view = data.get('view')
            task = data.get('task')
            executionTime = data.get('executionTime')
            crontab = treatmentTime(executionTime)
            if not crontab:
                raise ValueError("cron表达式格式有误")
            res = AP.cron_task(jk.buildJob, crontab, task, name=task)
            try:
                cron_expression = executionTime
                options = Options()
                options.locale_code = 'zh_CN'
                descriptor = ExpressionDescriptor(cron_expression, options)
                description = descriptor.get_description()
                self.message = f"{task} 已加入定时任务. 执行描述: {description}"
            except Exception as e:
                self.message = f"{task} 已加入定时任务. 执行描述: {e}"
        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message)



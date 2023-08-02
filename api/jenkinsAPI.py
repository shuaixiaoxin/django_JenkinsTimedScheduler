"""

在任务构建时 jenkins会有一个静默期，具体在配置中可以看到 默认5秒左右：

构建无参数时：当你多个任务运行时间 间距小于静默期 那么任务会合并触发 也就是只有一个构建号信息
构建有参数时：当你多个任务运行时间 间距小于静默期不会合并触发 会单独创建构建信息（这里的构建参数必须是不一样的 如果一样那一样的参数会合并触发）

注1：这种情况很少，只是针对那种在静默期内运行多次同一任务jenkins、同一参数才会触发合并
注2：如果不想合并触发，那在jenkins配置中可以把静默时间（生成前等待时间）改为0即可
"""

from jenkins import Jenkins
from django_JenkinsTimedScheduler import settings


class JenkinsApi:
    _url = settings.JENKINS_URL[0]

    def __init__(self, user, token):
        self.user = user
        self.token = token

    def handle_exception(func):
        def inner(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return 0, result
            except Exception as e:
                return 1, str(e)
        return inner

    @handle_exception
    def getWhomai(self):
        """
        :return: 当前用户信息
        """
        self.server = Jenkins(url=self._url, username=self.user, password=self.token)
        return self.server.get_whoami()

    @handle_exception
    def getView(self):
        """

        :return: 视图信息
        """
        self.server = Jenkins(url=self._url, username=self.user, password=self.token)
        return self.server.get_views()

    @handle_exception
    def getViewName(self, jobName):
        """

        :return: 视图下jobs
        """
        self.server = Jenkins(url=self._url, username=self.user, password=self.token)
        return self.server._get_view_jobs(jobName)

    @handle_exception
    def getCount(self):
        """
        :return: job数量
        """
        self.server = Jenkins(url=self._url, username=self.user, password=self.token)
        return self.server.jobs_count()

    @handle_exception
    def getJobs(self):
        """
        :return: 所有jobs信息
        """
        self.server = Jenkins(url=self._url, username=self.user, password=self.token)
        return self.server.get_jobs()

    def buildJob(self, jobName, parameters=None):
        """
        :param jobName: 构建job名字
        :param parameters: 构建参数
        :return: 构建信息
        """
        self.server = Jenkins(url=self._url, username=self.user, password=self.token)
        self.server.build_job(name=jobName, parameters=parameters)


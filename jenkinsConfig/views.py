import json
from urllib import request, error

from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer

from user.response import CustomResponse
from .serializers import UserTokenSerializer
from .models import UserToken


def check_url_availability(url):
    try:
        response = request.urlopen(url, timeout=1)
        print(f"The URL {url} is reachable.")
        return True
    except error.URLError as e:
        if isinstance(e.reason, str) and 'Forbidden' in e.reason:
            print(f"The URL {url} is not reachable. Error: {e.reason}")
            return True
        else:
            print(f"The URL {url} is not reachable. Error: {e.reason}")
            return False


class JenkinsListView(viewsets.ViewSet):
    """
    list: 列出Jenkins Url
    availability: 检测可用性
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = 200
        self.message = 'OK'
        self.data = None
        self.DataCount = None

    def jenkins_url(self, request):
        return CustomResponse(code=self.code, message=self.message, template_name='jenkins/jenkins-url.html')

    def list(self, request):
        data = []
        jenkinsList = settings.JENKINS_URL
        for i in jenkinsList:
            jenkinsDict = {}
            jenkinsDict['url'] = i
            data.append(jenkinsDict)
        self.data = data
        return CustomResponse(code=self.code, message=self.message, data=self.data)

    def availability(self, request):
        try:
            self.message = '该Jenkins Url可用'
            data = request.data
            if not check_url_availability(data.get('url')):
                self.code, self.message = 400, '该Jenkins Url不可用'
        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message)


class JenkinsTokenView(viewsets.ViewSet):
    """
    list: 列出token
    create: 创建token
    update: 更新token
    destroy: 删除token
    availability: 检测token可用性
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = 200
        self.message = 'OK'
        self.data = None
        self.DataCount = None

    def token_page(self, request):
        return CustomResponse(code=self.code, message=self.message, template_name='jenkins/jenkins-token.html')

    def token_add_page(self, request):
        return CustomResponse(code=self.code, message=self.message, template_name='jenkins/token-add.html')

    def list(self, request):
        try:
            user_token = UserToken.objects.get(user=request.user)
            serializer = UserTokenSerializer(user_token)
            token = serializer.data.get('token')
            data = [{'username': request.user.username, 'token': token}]
            return CustomResponse(code=self.code, message=self.message, data=data)
        except UserToken.DoesNotExist:
            return CustomResponse(code=self.code, message=self.message, status=201)

    def create(self, request):
        try:
            self.message = '令牌添加成功'
            data = request.data
            token = data.get('token')
            if token:
                if UserToken.objects.filter(user=request.user).exists():
                    self.code, self.message = 400, '当前用户已存在令牌'
                else:
                    serializer = UserTokenSerializer(data={'token': token, 'user': request.user.id})
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
            else:
                self.code, self.message = 400, '未接收到token'
            return CustomResponse(code=self.code, message=self.message)
        except Exception as e:
            return CustomResponse(code=400, message=str(e), status=400)

    def update(self, request):
        try:
            self.message = '令牌修改成功'
            data = request.data
            token = data.get('token')
            if token:
                user = UserToken.objects.get(user_id=request.user.id)
                serializer = UserTokenSerializer(instance=user, data={'token': token}, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
            else:
                self.code, self.message = 400, '未接收到token'
            return CustomResponse(code=self.code, message=self.message)
        except Exception as e:
            return CustomResponse(code=400, message=str(e), status=400)

    def destroy(self, request):
        try:
            self.message = '令牌删除成功'
            data = request.query_params.get('data')
            if data:
                for t in json.loads(data):
                    UserToken.objects.filter(token=t.get('token')).delete()
            else:
                self.code, self.message = 400, '未接收到token'
            return CustomResponse(code=self.code, message=self.message)
        except Exception as e:
            return CustomResponse(code=400, message=str(e), status=400)

    def availability(self, request):
        try:
            self.message = '该Token可用'
            data = request.data
            token = data.get('token')
            if token:
                pass
            else:
                self.code, self.message = 400, '未接收到token'
            return CustomResponse(code=self.code, message=self.message)
        except Exception as e:
            return CustomResponse(code=400, message=str(e), status=400)

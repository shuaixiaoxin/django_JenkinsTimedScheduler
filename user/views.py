import json
import re

from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.shortcuts import redirect

from rest_framework import viewsets
from rest_framework import serializers
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import LoginSerializer, UserSerializer
from .response import CustomResponse
from menu.views import add_default_menus_to_user
from menu.models import Menu, UserMenu


class LoginView(viewsets.ViewSet):
    """
    get_permissions: 权限重写
    login_page: 返回登录模板
    login: 验证用户逻辑
    user_logout： 用户退出
    homeAPI： 首页的逻辑
    """
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def get_permissions(self):
        if self.action in ['login_page', 'login']:
            return [AllowAny()]
        else:
            return [IsAuthenticated()]

    def login_page(self, request):
        return CustomResponse(code=200, message='OK', template_name='login/login.html')

    def login(self,request):
        if request.method == 'POST':
            serializer = LoginSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
                user = serializer.validated_data['user']
                login(request, user)
                # refresh = RefreshToken.for_user(user)
                # userToken = {}
                # userToken["refresh"] = str(refresh)
                # userToken["access_token"] = str(refresh.access_token)
                return CustomResponse(code=200, message='Logged in successfully.', template_name='index.html')

            except serializers.ValidationError as e:
                error_dict = e.detail
                first_error = next(iter(error_dict.values()))[0]
                msg = first_error if first_error else None
                return CustomResponse(code=400, message=msg, template_name='login/login.html')
        else:
            if not request.user.is_authenticated:
                return CustomResponse(code=200, message='Disallowed request.', template_name='login/login.html')
            else:
                return CustomResponse(code=200, message='Refresh page.', template_name='index.html')

    def user_logout(self, request):
        logout(request)
        request.session.flush()
        return redirect('login')

    def homeAPI(self, request):
        return CustomResponse(code=200, message='', template_name='homepage.html')


class UserView(viewsets.ViewSet):
    """
    list: 所有用户信息
    create: 创建用户
    update: 更新用户
    destroy: 删除用户
    active: 启用/禁用用户
    user_menu: 用户菜单树
    userMenuAPI: 授权菜单api
    """

    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = 200
        self.message = 'OK'
        self.data = None
        self.DataCount = None

    def users_page(self, request):
        return CustomResponse(code=200, message='OK', template_name='user/user-management.html')

    def user_add_page(self, request):
        return CustomResponse(code=200, message='OK', template_name='user/user-add.html')

    def user_update_page(self, request):
        return CustomResponse(code=200, message='OK', template_name='user/user-update.html')

    def user_menu_page(self, request):
        return CustomResponse(code=200, message='OK', template_name='user/user-menu.html')

    def list(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        self.data = serializer.data
        return CustomResponse(code=self.code, message=self.message, data=self.data)

    def create(self, request):
        try:
            data = request.data
            username = data.get('username')
            zh_username = data.get('zh_username')
            password1 = data.get('password1')
            password2 = data.get('password2')
            email = data.get('email')
            perm = data.get('perm')
            user_exists = User.objects.filter(username=username).exists()
            if user_exists:
                self.code, self.message = 400, '%s 用户已存在' % username
            elif password1 != password2:
                self.code, self.message = 400, '两次密码不一致'
            elif len(password1) < 8 or len(password1) > 16:
                self.code, self.message = 400, '密码长度应大于8小于16'
            elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$', password1):
                self.code, self.message = 400, '密码至少包含数字、小写字母、大写字母'
            if self.code == 200:
                if perm == 'super_user':
                    User.objects.create_superuser(username=username, email=email, password=password1, first_name=zh_username)
                else:
                    user = User.objects.create_user(username=username, email=email, password=password1, first_name=zh_username)
                    add_default_menus_to_user(user)

        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message)

    def update(self, request):
        try:
            data = request.data
            userId = data.get('userId')
            username = data.get('username')
            zh_username = data.get('zh_username')
            password = data.get('password')
            email = data.get('email')
            if password:
                if len(password) < 8 or len(password) > 16:
                    self.code, self.message = 400, '密码长度应大于8小于16'
                elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$', password):
                    self.code, self.message = 400, '密码至少包含数字、小写字母、大写字母'
                update_data = {'username': username, 'first_name': zh_username, 'email': email}
                User.objects.filter(pk=userId).update(**update_data)
                user = User.objects.get(pk=userId)
                user.set_password(password)
                user.save()
            else:
                update_data = {'username': username, 'first_name': zh_username, 'email': email}
                User.objects.filter(pk=userId).update(**update_data)

        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message)

    def destroy(self, request):
        try:
            userId = []
            self.message = 'User Delete Success.'
            data = request.query_params.get('data')
            if data:
                for i in json.loads(data):
                    userId.append(i['id'])
            else:
                self.message = 'not found params.'
            if userId:
                User.objects.filter(id__in=userId).delete()
        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message)

    def active(self, request):
        try:
            data = request.data
            if data:
                if data.get('active') == 'false':
                    user = User.objects.get(id=data.get('userId'))
                    user.is_active = False
                    user.save()
                    self.message = '用户已禁用'
                else:
                    user = User.objects.get(id=data.get('userId'))
                    user.is_active = True
                    user.save()
                    self.message = '用户已启用'
            else:
                self.message = 'not found params.'
        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message)

    def user_menu(self, request):
        try:
            userId = request.query_params.get('userId')
            menu_data = []
            root_menus = Menu.objects.filter(parent=None).order_by('order')

            for root_menu in root_menus:
                menu_item = {
                    'title': root_menu.name,
                    'id': root_menu.id,
                    'spread': 'true',
                    'children': []
                }

                child_menus = root_menu.children.all().order_by('order')

                for child_menu in child_menus:
                    child_menu_item = {
                        'title': child_menu.name,
                        'id': child_menu.id
                    }

                    # 检查当前用户是否有子菜单权限
                    if UserMenu.objects.filter(user_id=userId, menu=child_menu).exists():
                        child_menu_item['checked'] = 'true'

                    menu_item['children'].append(child_menu_item)

                menu_data.append(menu_item)
            self.data = menu_data
        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message, data=self.data)

    def userMenuAPI(self, request):
        try:
            data = request.data
            if data:
                userId = data.get('userId')
                menu_data = data.get('menu')
                user = User.objects.get(id=userId)
                user_menus = UserMenu.objects.filter(user=user)
                user_menus.delete()
                for menu_item in menu_data:
                    menu_id = menu_item['id']
                    children = menu_item.get('children', [])
                    user_menu, created = UserMenu.objects.get_or_create(user=user, menu_id=menu_id)

                    for child_menu_item in children:
                        child_menu_id = child_menu_item['id']

                        # 给用户添加子菜单权限
                        user_child_menu, created = UserMenu.objects.get_or_create(user=user, menu_id=child_menu_id)
                        user_child_menu.save()
        except Exception as e:
            self.code, self.message = 400, str(e)
        return CustomResponse(code=self.code, message=self.message)

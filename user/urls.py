"""

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import UserView, LoginView
from rest_framework_simplejwt.views import TokenRefreshView


# 重新刷新token返回值
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.data['code'] = 200
        response.data['message'] = 'Refreshing the token succeeded.'
        data = {'access': response.data.pop('access')}
        response.data['data'] = data

        return response


urlpatterns = [
    path('', LoginView.as_view({'get': 'login_page'}), name='login'),
    path('login', LoginView.as_view({'get': 'login_page'}), name='login'),
    path('jenkins', LoginView.as_view({'get': 'login', 'post': 'login'}), name='jenkins'),
    path('user-logout', LoginView.as_view({'get': 'user_logout'}), name='logout'),
    path('homepage', LoginView.as_view({'get': 'homeAPI'}), name='homepage'),

    path('users', UserView.as_view({'get': 'users_page'}), name='users'),
    path('user-add', UserView.as_view({'get': 'user_add_page'}), name='userAddPage'),
    path('user-update', UserView.as_view({'get': 'user_update_page'}), name='userUpdatePage'),
    path('user-menu', UserView.as_view({'get': 'user_menu_page'}), name='userMenuPage'),
    path('users/user-list', UserView.as_view({'get': 'list'}), name='userList'),
    path('users/user-create', UserView.as_view({'post': 'create'}), name='userCreate'),
    path('users/user-update', UserView.as_view({'put': 'update'}), name='userUpdate'),
    path('users/user-delete', UserView.as_view({'delete': 'destroy'}), name='userDelete'),
    path('users/user-active', UserView.as_view({'post': 'active'}), name='userActive'),
    path('users/user-menu', UserView.as_view({'get': 'user_menu'}), name='userMenu'),
    path('users/user-menuAPI', UserView.as_view({'post': 'userMenuAPI'}), name='userMenuAPI'),

    path('api/token/refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),




]

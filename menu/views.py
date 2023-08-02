from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer

from .models import Menu, UserMenu
from user.response import CustomResponse
from .serializers import MenuSerializer


class MenuAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.is_superuser:
            menus = Menu.objects.order_by('order')
        else:
            user_menus = UserMenu.objects.filter(user_id=request.user.id).values_list('menu_id', flat=True)
            menus = Menu.objects.filter(id__in=user_menus).order_by('order')

        menu_dict = {}

        # 取出父菜单
        for menu in menus:
            if menu.parent_id is None:
                menu_dict[menu.id] = {
                    'title': menu.name,
                    'icon': 'fa fa-server',
                    'href': '',
                    'target': '_self',
                    'child': []
                }

        # 往父菜单中加子菜单
        for menu in menus:
            if menu.parent_id is not None:
                parent_menu = menu_dict.get(menu.parent_id)
                if parent_menu is not None:
                    parent_menu['child'].append({
                        'title': menu.name,
                        'icon': 'fa fa-heart',
                        'href': menu.url,
                        'target': '_self'
                    })

        menu_list = menu_dict.values()
        level = {"title": "调度平台", "icon": "fa fa-address-book", "href": "", "id": '1', "target": "_self", "child": menu_list}
        homeinfo = {"title": "首页", "href": "homepage"}
        logoinfo = dict(title="调度平台", image="static/layuimini/images/logo.png", href="")
        menu_info = {"homeInfo": homeinfo, "logoInfo": logoinfo, 'menuInfo': [level]}

        return Response(menu_info)


# 用户绑定默认菜单
def add_default_menus_to_user(user):
    default_menu_ids = settings.MENU_ID

    default_menus = Menu.objects.filter(id__in=default_menu_ids)
    for default_menu in default_menus:
        UserMenu.objects.create(user=user, menu=default_menu)


class MenuView(viewsets.ViewSet):
    """
    list: 所有菜单信息
    """
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def menus_page(self, request):
        return CustomResponse(code=200, message='OK', template_name='menu/menu-management.html')

    def list(self, request):
        menu = Menu.objects.all()
        serializer = MenuSerializer(menu, many=True)
        return CustomResponse(code=200, message='OK', data=serializer.data)

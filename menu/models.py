from django.db import models
from django.contrib.auth.models import Group, User
# Create your models here.


class Menu(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 't_menus'
        verbose_name = '菜单详情'
        verbose_name_plural = verbose_name


class UserMenu(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)

    db_table = 't_usermenus'
    verbose_name = '用户菜单'
    verbose_name_plural = verbose_name


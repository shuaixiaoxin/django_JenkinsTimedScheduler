from django.contrib import admin
from django.contrib import admin
from .models import UserToken
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
admin.site.site_title = '任务调度系统'
admin.site.site_header = 'Jenkins 任务调度系统'
admin.site.index_title = 'Jenkins 任务调度系统'


User = get_user_model()


class MyModelAdmin(admin.ModelAdmin):
    list_display = ('token', 'user')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(user=request.user)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['user'].queryset = User.objects.filter(pk=request.user.pk)
        return form


admin.site.register(UserToken, MyModelAdmin)

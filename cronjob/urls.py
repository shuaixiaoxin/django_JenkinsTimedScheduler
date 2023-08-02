"""django_JenkinsTimedScheduler URL Configuration

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
from .views import JenkinsCronOneView, JenkinsCronCycleView

urlpatterns = [
    path('cron-once', JenkinsCronOneView.as_view({'get': 'cron_one_page'}), name='cronOne'),
    path('view-group-api', JenkinsCronOneView.as_view({'post': 'viewGroupAPI'}), name='viewGroup'),
    path('Timed-execution', JenkinsCronOneView.as_view({'post': 'TimedExecution'}), name='TimedExecution'),

    path('cron-cycle', JenkinsCronCycleView.as_view({'get': 'cron_cycle_page'}), name='cronCycle'),
    path('Cycle-Timed-execution', JenkinsCronCycleView.as_view({'post': 'CycleTimedExecution'}), name='CycleTimedExecution'),
]

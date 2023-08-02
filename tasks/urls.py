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
from .views import JenkinsTaskListView, JenkinsTaskHistoryView

urlpatterns = [
    path('task-list', JenkinsTaskListView.as_view({'get': 'tasksListPage'}), name='taskPage'),
    path('task-list-api', JenkinsTaskListView.as_view({'get': 'taskListAPI'}), name='taskList'),
    path('task-pause-api', JenkinsTaskListView.as_view({'post': 'paused_task'}), name='paused'),
    path('task-resume-api', JenkinsTaskListView.as_view({'post': 'resumed_task'}), name='resumed'),
    path('task-remove-api', JenkinsTaskListView.as_view({'post': 'remove_task'}), name='removed'),

    path('history-list', JenkinsTaskHistoryView.as_view({'get': 'tasksHistoryPage'}), name='historyPage'),
    path('history-list-api', JenkinsTaskHistoryView.as_view({'get': 'historyListAPI'}), name='historyList'),
    path('history-list-delete', JenkinsTaskHistoryView.as_view({'post': 'deleteHistory'}), name='historyDelete'),
]

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
from .views import JenkinsListView, JenkinsTokenView

urlpatterns = [
    path('jenkins-token', JenkinsTokenView.as_view({'get': 'token_page'}), name='token'),
    path('jenkins-list', JenkinsListView.as_view({'get': 'jenkins_url'}), name='jenkinsUrl'),
    path('jenkins-list-api', JenkinsListView.as_view({'get': 'list'}), name='jenkinsUrlApi'),
    path('jenkins-list-availability', JenkinsListView.as_view({'post': 'availability'}), name='jenkinsUrlAvailability'),
    path('jenkins-token-list', JenkinsTokenView.as_view({'get': 'list'}), name='tokenList'),
    path('jenkins-token-add', JenkinsTokenView.as_view({'get': 'token_add_page'}), name='tokenAdd'),
    path('jenkins-token-add-api', JenkinsTokenView.as_view({'post': 'create'}), name='tokenAddApi'),
    path('jenkins-token-update-api', JenkinsTokenView.as_view({'put': 'update'}), name='tokenUpdateApi'),
    path('jenkins-token-destroy-api', JenkinsTokenView.as_view({'delete': 'destroy'}), name='tokenDestroyApi'),
    path('jenkins-token-availability-api', JenkinsTokenView.as_view({'post': 'availability'}), name='tokenAvailabilityApi'),
]

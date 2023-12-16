"""
URL configuration for askme_klenov project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from app import views as app_views
from askme_klenov import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', app_views.index, name='index'),
    path('login/', app_views.login, name='login'),
    path('signup/', app_views.signup, name='signup'),
    path('ask/', app_views.ask, name='ask'),
    path('hot/', app_views.hot, name='hot'),
    path('question/<int:question_id>', app_views.question, name='question'),
    path('tag/<str:tag_name>', app_views.tag_index, name='tag'),
    path('settings/', app_views.settings, name='settings'),
    path('404', app_views.not_found, name='not_found')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
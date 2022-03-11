from django.contrib import admin
from django.urls import path
from .views import get_sys_info, get_status_info
from rest_framework.routers import SimpleRouter

router = SimpleRouter()


urlpatterns = [
    path('sysinfo/', get_sys_info),
    path('status/', get_status_info)
] + router.urls


print('=' * 30)
print(urlpatterns)
print('=' * 30)
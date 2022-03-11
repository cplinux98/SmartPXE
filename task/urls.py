from django.contrib import admin
from django.urls import path
from task.views import TaskListViewSet, TaskResultSerializerViewSet, PlaybookTempSerializerViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('hostlist', TaskListViewSet)
router.register('template', PlaybookTempSerializerViewSet)
router.register('result', TaskResultSerializerViewSet)

urlpatterns = [
] + router.urls


print('=' * 30)
print(urlpatterns)
print('=' * 30)

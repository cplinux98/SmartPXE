from django.contrib import admin
from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import ImageTempViewSet, upload, OSTempViewSet, publickey, extract_image

router = SimpleRouter()
router.register('image', ImageTempViewSet)
router.register('config', OSTempViewSet)

urlpatterns = [
    # path('upload/', upload),
    path('extract/', extract_image),
    path('publickey/', publickey)
] + router.urls


print('=' * 30)
print(urlpatterns)
print('=' * 30)

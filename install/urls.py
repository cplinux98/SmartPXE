from django.contrib import admin
from django.urls import path
from install.views import DiscoverViewSet, InstallPreListViewSet, InstallProgressViewSet, InstallResultViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('discover', DiscoverViewSet)
router.register('iprelist', InstallPreListViewSet)
router.register('progress', InstallProgressViewSet)
router.register('result', InstallResultViewSet)

urlpatterns = [
] + router.urls


print('=' * 30)
print(urlpatterns)
print('=' * 30)
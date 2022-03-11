from rest_framework import serializers
from .models import Discover, InstallPreList, InstallProgress, InstallResult


class DiscoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discover
        fields = '__all__'


class InstallPreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallPreList
        fields = '__all__'


class InstallProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallProgress
        fields = '__all__'


class InstallResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallResult
        fields = '__all__'


# class IStatusSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IStatus
#         fields = '__all__'


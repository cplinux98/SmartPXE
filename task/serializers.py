from rest_framework import serializers
from .models import TaskList, TaskResult, PlaybookTemp


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskList
        fields = '__all__'


class TaskResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskResult
        fields = '__all__'


class PlaybookTempSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaybookTemp
        fields = '__all__'


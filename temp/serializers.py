from rest_framework import serializers
from .models import ImageTemp, OSTemp


class ImageTempSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageTemp
        fields = '__all__'


class OSTempSerializer(serializers.ModelSerializer):
    class Meta:
        model = OSTemp
        fields = '__all__'


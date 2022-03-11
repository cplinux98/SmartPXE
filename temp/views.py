import json

from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from .models import ImageTemp, OSTemp
from .serializers import ImageTempSerializer, OSTempSerializer
from rest_framework.decorators import api_view, action, permission_classes
from django.core.files.uploadedfile import InMemoryUploadedFile
from install.serializers import InstallPreListSerializer
from pathlib import Path
from django.conf import settings
from datetime import datetime
from uuid import uuid4
import os
import shutil
from utils.tools import replace_ks_url
from rest_framework import status
from rest_framework.response import Response
from django.db import transaction
from rest_framework.settings import api_settings


class ImageTempViewSet(ModelViewSet):
    queryset = ImageTemp.objects.all()
    serializer_class = ImageTempSerializer

    def destroy(self, request, *args, **kwargs):
        # 删除镜像时，先判断镜像是否存在，如果存在则删除
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        file_path = Path(serializer.data['save_path'])
        if file_path and Path.exists(file_path):
            try:
                instance.delete()
                shutil.rmtree(file_path, ignore_errors=True)
                return Response(status=204)
            except:
                return Response({'code': 888, 'message': '镜像删除失败，请检查关联系统模板是否删除！'})
        else:
            return Response({'code': 888, 'message': '镜像删除失败，镜像在系统中不存在！'})


class OSTempViewSet(ModelViewSet):
    queryset = OSTemp.objects.all()
    serializer_class = OSTempSerializer

    @classmethod
    def write_file(cls, save_path, config):
        Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
        with open(save_path, 'wb+') as f:
            f.write(config)
        return 1

    def create(self, request, *args, **kwargs):
        """ 1. save and check"""
        with transaction.atomic():
            image_name = request.data["image"]
            ks_name = request.data["name"]
            ks_content = request.data["config"].encode("UTF-8")
            path = '{}/ks/{}/{}.ks'.format(settings.SERVER_URL, image_name, ks_name)
            save_path = os.path.join(settings.KS_DIR, image_name, "{}.ks".format(ks_name))
            request.data["path"] = path
            request.data["save_path"] = save_path
            ret = super().create(request, *args, **kwargs)
            self.write_file(save_path, ks_content)
            return ret

    def destroy(self, request, *args, **kwargs):
        # 删除记录时应该判断一下KS文件是否存在，如果存在应该将KS文件一起删除
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        ks_path = serializer.data['save_path']
        print(ks_path)
        self.perform_destroy(instance)
        if ks_path and Path(ks_path).exists():
            os.remove(Path(ks_path))
        return Response(status=204)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.save():
            file_name = serializer.data['save_path']
            config = serializer.data['config'].encode("utf-8")
            with open(Path(file_name), 'wb+') as fd:
                fd.write(config)

        return Response(serializer.data)

    @action(['post'], detail=False, url_path="generate")
    def generate_ks(self, request, *args, **kwargs):
        obj = ImageTemp.objects.all().filter(name__exact=request.data['image'])
        image_info = ImageTempSerializer(obj, many=True).data[0]
        print(image_info, type(image_info))
        image_path = image_info['path']
        old_config = request.data['config']
        new_config = replace_ks_url(old_config, image_path, settings.SERVER_API)
        # 记得替换
        code = new_config[0]
        message = new_config[1]
        if code:
            return Response(message)
        else:
            return Response({'code': 888, 'message': message})

# @permission_classes([IsAuthenticated])
@api_view(['POST'])
def extract_image(request: Request):
    data = request.data
    image_path = data['path']
    image_name = data['name']
    image_type = data['type']
    image_version = data['version']
    if not Path(image_path).exists():
        return Response({'code': 888, 'message': '镜像不存在'})
    if Path(image_path).suffix != '.iso':
        return Response({'code': 888, 'message': '请检查镜像格式'})
    os.popen("mount -o loop {} /media".format(image_path)).read()
    save_path = Path('/var/www/html/images/{}/{}/{}/'.format(image_type, image_version, image_name))
    save_path.mkdir(parents=True, exist_ok=True)
    os.popen("rsync -a /media/ {}".format(save_path)).read()
    os.popen("umount /media").read()
    dest_url = '{}/images/{}/{}/{}'.format(settings.SERVER_URL, image_type, image_version, image_name)

    return Response({'name': image_name, 'url': dest_url, 'save_path': str(save_path)})

# @permission_classes([IsAuthenticated])
@api_view(['POST'])
def upload(request: Request):
    file_fields_name = 'file'
    file_obj: InMemoryUploadedFile = request.data.get(file_fields_name)
    print(file_obj.name)
    print(request.data)
    print('~' * 30)
    uploads_dir = Path(settings.IMAGES_UPLOADS_DIR)
    parent_dir = Path("{:%Y/%m/%d}".format(datetime.now()))
    (uploads_dir / parent_dir).mkdir(parents=True, exist_ok=True)
    filename = Path(uuid4().hex + '.iso')
    temp_path = uploads_dir / parent_dir / filename
    with open(temp_path, 'wb') as f:
        for c in file_obj.chunks():
            f.write(c)
    print(temp_path)

    os.popen("mount -o loop {} /media".format(temp_path)).read()
    type = request.data['type']
    version = request.data['version']
    name = request.data['name']
    save_path = Path('/var/www/html/images/{}/{}/{}/'.format(type, version, name))
    save_path.mkdir(parents=True, exist_ok=True)
    os.popen("rsync -a /media/ {}".format(save_path)).read()
    os.popen("umount /media").read()
    if Path.exists(temp_path):
        os.remove(temp_path)

    dest_url = '{}/images/{}/{}/{}'.format(settings.SERVER_URL, type, version, name )

    return Response({'name': file_obj.name, 'url': dest_url, 'save_path': str(save_path)})



# @permission_classes([])
@api_view(['GET'])
def publickey(request):
    key = settings.PUBLIC_KEY.replace('\"', '')
    return Response(key)





# @api_view(['POST'])
# def generate_standard_config(request: Request):
#     """
#     :param: config , image , name
#     :return: file_url
#     根据发送过来的ks配置信息，镜像id， name，去生成标准的ks配置信息
#     """
#
#     obj = ImageTemp.objects.all().filter(name__exact=request.data['image'])
#     image_info = ImageTempSerializer(obj, many=True).data[0]
#     print(image_info, type(image_info))
#     image_path = image_info['path']
#     image_name = image_info['name']
#     file_name = request.data['name']
#     old_config = request.data['config']
#     new_config = replace_ks_url(old_config, image_path, settings.SERVER_API)
#     # 记得替换
#     print(new_config)
#     code, message = new_config[0], new_config[1]
#     if code:
#         return Response(message)
#     return Response({"code": code, "message": message})
#



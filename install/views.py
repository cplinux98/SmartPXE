from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.views import Response, Request
from utils.tools import generate_pxe_menu, send_run_rom_scripts, ManagerDnsmasq

from rest_framework.viewsets import ModelViewSet
from .serializers import DiscoverSerializer, InstallPreListSerializer, InstallProgressSerializer, InstallResultSerializer
from .models import Discover, InstallPreList, InstallProgress, InstallResult
from rest_framework.decorators import action
from django.db import transaction
from task.serializers import TaskListSerializer
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from pathlib import Path
import os
from task.models import TaskList
from task.serializers import TaskListSerializer


class DiscoverViewSet(ModelViewSet):
    queryset = Discover.objects.all()
    serializer_class = DiscoverSerializer

    @action(methods=['POST'], detail=True, url_path='convert/(?P<target>\d+)')
    def host_status_convert(self, request:Request, pk, target):
        # 这个是转换的api，发送 要转换的pk 和 要转换到哪个表
        print(target) # 1: task_pre , 2: install_pre
        obj = self.get_object()
        serializer = DiscoverSerializer(obj)
        data = serializer.data
        print('=' * 30)
        print(target, type(target))
        if target == '2':
            print('~' * 30)
            toserializer = InstallPreListSerializer(data=data)
            validated = toserializer.is_valid(raise_exception=True)
            toserializer.save()
            print(toserializer.data)
            obj.delete()
        if target == '1':
            toserializer = TaskListSerializer(data=data)
            validated = toserializer.is_valid(raise_exception=True)
            toserializer.save()
            obj.delete()
        return Response(status=201)


# class IStatusViewSet(ModelViewSet):
#     queryset = IStatus.objects.all()
#     serializer_class = IStatusSerializer

class InstallPreListViewSet(ModelViewSet):
    queryset = InstallPreList.objects.all()
    serializer_class = InstallPreListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    @action(methods=['POST'], detail=True, url_path='convert')
    def convert_to_install(self, request:Request, pk):
        # 这个是转换的api，发送 要转换的pk 和 要转换到install_pre
        with transaction.atomic():
            obj = self.get_object()
            serializer = InstallPreListSerializer(obj)
            data = serializer.data
            toserializer = TaskListSerializer(data=data)
            validated = toserializer.is_valid(raise_exception=True)
            toserializer.save()
            obj.delete()
            return Response(status=201)


    @action(detail=False, url_path='allmac')
    def get_all_mac(self, request):
        all_obj = self.get_queryset().filter().values('sn', 'mac', 'os', 'config')
        print(all_obj)

        # serializer = InstallPreListSerializer(all_obj)
        # data = serializer.data
        # print(data)
        return Response(all_obj)

    # 拦截patch方法，修改后，根据条目里的config 生成pxe菜单，再填充数据库

    def partial_update(self, request: Request, *args, **kwargs):
        # 在这里生成pxe菜单
        print(request.data)
        print(kwargs)
        _config = request.data['config']
        if isinstance(_config, str):
            from temp.serializers import CustomOSTempSerializer
            from temp.models import CustomOSTemp
            config_obj = CustomOSTemp.objects.filter(name=_config).values('image', 'path', 'name')[0]
        else:
            config_obj = _config
        ks_path = config_obj['path']
        image = config_obj['image']
        ks_name = config_obj['name']
        from temp.models import ImageTemp
        # all_obj = self.get_queryset().all().values('sn', 'mac', 'os', 'config')
        # print(all_obj)
        get_image_path = ImageTemp.objects.filter(name=image).values('name', 'path')
        image_info = get_image_path[0]
        image_kernel = image_info['path'] + '/isolinux/vmlinuz'
        image_initrd = image_info['path'] + '/isolinux/initrd.img'
        image_name = image_info['name']
        print(image_kernel, image_initrd, image_name, ks_path)
        pxe_menu_path = generate_pxe_menu(kwargs['pk'], image_kernel, image_initrd, ks_path, option='')

        path_info = {
            'os': image_name,
            'config': ks_name,
            'pxe_menu_path': pxe_menu_path
        }
        print('~' * 30)
        class NewRequest:
            def __init__(self, data):
                self.data = data

        newrequest = NewRequest(path_info)
        print(newrequest, newrequest.data)

        return super().partial_update(newrequest, *args, **kwargs)

    @action(methods=['POST'], detail=True, url_path='install')
    def host_status_to_install(self, request: Request, pk):
        # 修改主机状态为安装状态，并且添加mac地址绑定ip
        obj = self.get_object()
        serializer = InstallPreListSerializer(obj)
        data = serializer.data
        if data['os'] is None or data['config'] is None:
            return Response({'code': 800, 'message': '该设备未关联模板'})
        obj_ip = data['clientip']
        data['status_id'] = '1'
        data['status_progress'] = '5%'
        data['status_content'] = "[{}] - [{}]".format(datetime.now(), '向客户端发送指令成功')
        print(data)
        toserializer = InstallProgressSerializer(data=data)
        if toserializer.is_valid(raise_exception=True):
            toserializer.save()
            ManagerDnsmasq().add(data['mac'], obj_ip)
            obj.delete()
            return Response(status=201)

    def destroy(self, request, *args, **kwargs):
        # 删除记录时应该判断一下菜单文件是否存在，如果存在应该将菜单文件一起删除
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        menu_path = serializer.data['pxe_menu_path']
        print(menu_path)
        if menu_path and Path(menu_path).exists():
            os.remove(Path(menu_path))
        self.perform_destroy(instance)
        return Response(status=204)


class InstallProgressViewSet(ModelViewSet):
    queryset = InstallProgress.objects.all()
    serializer_class = InstallProgressSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['mac']

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_serializer = self.get_serializer(instance)
        old_data = old_serializer.data
        print(old_data)
        old_content = old_data['status_content'] + '\n'
        _new_content = "[{}] - [{}]".format(datetime.now(), request.data['status_content'])
        new_content = old_content + _new_content
        request.data['status_content'] = new_content
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(methods=['POST'], detail=True, url_path='finished/(?P<status>\d+)')
    def finished(self, request, pk, status):
        # 进度完成接口，将该条记录迁移至安装记录中，并增加安装状态
        obj = self.get_object()
        serializer = InstallProgressSerializer(obj)
        data = serializer.data
        print(data)
        data['status'] = status
        print(status)
        toserializer = InstallResultSerializer(data=data)
        if toserializer.is_valid(raise_exception=True):
            toserializer.save()
            mac = data['mac']
            ManagerDnsmasq().delete(mac)
            menu_path = data['pxe_menu_path']
            if menu_path and Path(menu_path).exists():
                os.remove(Path(menu_path))
            obj.delete()
            return Response(status=201)

    @action(methods=['POST'], detail=True, url_path='termination/(?P<status>\d+)')
    def termination(self, request, pk, status):
        # 终止安装，将该条记录迁移至安装记录中，并增加终止状态
        # 0：终止安装，并关机； 1：终止安装，并重启
        obj = self.get_object()
        serializer = InstallProgressSerializer(obj)
        data = serializer.data
        data['status'] = 0
        print(status)
        new_content = data['status_content'] + '\n' + "[{}] - [{}]".format(datetime.now(), "操作手动终止！")
        data['status_content'] = new_content
        if status:
            send_run_rom_scripts(data['clientip'], "reboot", "root", '')
        else:
            send_run_rom_scripts(data['clientip'], "showdown", "root", '')
        toserializer = InstallResultSerializer(data=data)
        if toserializer.is_valid(raise_exception=True):
            toserializer.save()
            mac = data['mac']
            ManagerDnsmasq().delete(mac)
            menu_path = data['pxe_menu_path']
            if menu_path and Path(menu_path).exists():
                os.remove(Path(menu_path))
            obj.delete()
            return Response(status=201)

    def destroy(self, request, *args, **kwargs):
        """
        处理手动删除记录
        """
        obj = self.get_object()
        serializer = InstallProgressSerializer(obj)
        data = serializer.data
        data['status'] = 0
        new_content = data['status_content'] + '\n' + "[{}] - [{}]".format(datetime.now(), "手动删除记录！")
        data['status_content'] = new_content
        toserializer = InstallResultSerializer(data=data)
        if toserializer.is_valid(raise_exception=True):
            toserializer.save()
            mac = data['mac']
            ManagerDnsmasq().delete(mac)
            menu_path = data['pxe_menu_path']
            if menu_path and Path(menu_path).exists():
                os.remove(Path(menu_path))
            obj.delete()
            return Response(status=201)




class InstallResultViewSet(ModelViewSet):
    queryset = InstallResult.objects.all()
    serializer_class = InstallResultSerializer

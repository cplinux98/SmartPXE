import json

from django.shortcuts import render
from rest_framework.views import Response, Request
from rest_framework.viewsets import ModelViewSet
from .serializers import TaskListSerializer, TaskResultSerializer, PlaybookTempSerializer
from .models import TaskList, TaskResult, PlaybookTemp
from rest_framework.decorators import action
from utils.tools import RunAnsible
from django.db import transaction
from install.serializers import InstallPreListSerializer
import redis
# Create your views here.



class TaskListViewSet(ModelViewSet):
    queryset = TaskList.objects.all()
    serializer_class = TaskListSerializer

    @action(methods=['POST'], detail=True, url_path='convert')
    def convert_to_install(self, request:Request, pk):
        # 这个是转换的api，发送 要转换的pk 和 要转换到install_pre
        with transaction.atomic():
            obj = self.get_object()
            serializer = TaskListSerializer(obj)
            data = serializer.data
            toserializer = InstallPreListSerializer(data=data)
            validated = toserializer.is_valid(raise_exception=True)
            toserializer.save()
            obj.delete()
            return Response(status=201)

    @action(methods=['POST'], detail=True, url_path='command')
    def run_command(self, request: Request, pk):
        print(request.data)
        model = request.data['model']
        model_args = request.data['args']
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        data = serializer.data
        ipaddr = data['clientip']
        # ipaddr = "10.10.100.39"
        ret = RunAnsible(ipaddr).run_model(model, model_args)
        # ret = _ret.replace('\n', '<br />')
        return Response(ret)

    @action(methods=['POST'], detail=True, url_path='playbook')
    def run_playbook(self, request: Request, pk):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        data = serializer.data
        ipaddr = data['clientip']
        sn = data['sn']
        playbook_id = request.data['tempid']
        get_playbook_obj = PlaybookTemp.objects.filter(pk=playbook_id).values('name', 'content')
        # print(PlaybookTemp.objects.filter(pk=playbook_id)[0])
        playbook = get_playbook_obj[0].get('content')
        playbook_name = get_playbook_obj[0].get('name')
        from .tasks import run_playbook
        try:
            toserializer = TaskResultSerializer(data={
                "name": sn,
                "status": 1,
                "playbook": playbook_name,
                "result": "任务提交完成"
            })
            validated = toserializer.is_valid(raise_exception=True)
            toserializer.save()
            record_id = toserializer.data['id']
            run_playbook.delay(host=ipaddr, name=sn, playbook=playbook, record_id=record_id)

        except Exception as e:
            print(e)
            return Response('任务提交失败')
        return Response('任务已经提交')





class TaskResultSerializerViewSet(ModelViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer

    @action(methods=['GET'], detail=False, url_path='running')
    def get_running(self, request: Request):
        try:
            task_id = request.query_params.get('taskid')
            print(task_id)
            pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True, db=3)
            r = redis.Redis(connection_pool=pool)
            rdata = r.get(task_id)
            if not rdata:
                return Response({'code': 888, 'message': '任务执行已结束！'})
            ret = json.loads(rdata).get('message')
        except Exception as e:
            return Response({'code': 888, 'message': '任务执行已结束！'})
            # return Response({'code': 888, 'message': str(e)})
        # r.close()
        return Response(ret)

class PlaybookTempSerializerViewSet(ModelViewSet):
    queryset = PlaybookTemp.objects.all()
    serializer_class = PlaybookTempSerializer

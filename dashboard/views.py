import datetime

import psutil
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from install.models import Discover, InstallResult, InstallProgress

# get sys info
# @permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_sys_info(request: Request):
    options = {
        "cpu": psutil.cpu_percent(),
        "disk": psutil.virtual_memory().percent,
        "mem": psutil.disk_usage('/').percent
    }
    return Response(options)


# get status number
# @permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_status_info(request: Request):
    client_num = Discover.objects.all().count()
    install_num = InstallProgress.objects.all().count()
    success = InstallResult.objects.filter(status=1).count()
    failed = InstallResult.objects.filter(status=0).count()

    status = {
        "success": success,
        "failed": failed,
        "online": client_num,
        "running": install_num
    }

    return Response(status)


@api_view(['GET'])
def get_history_info(request: Request):
    """
    获取完成的，失败和成功的历史数据
    :param request:
    :return:
    """
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=30)

    select = {'day': 'date(date)'}

    success_module = InstallResult.objects.filter(status=1, date__range=(start_time, end_time)).extra(select)
    success = success_module.values('day').distinct().order_by('day').annotate(number=Count('date'))

    failed_module = InstallResult.objects.filter(status=0, date__range=(start_time, end_time)).extra(select)
    failed = failed_module.values('day').distinct().order_by('day').annotate(number=Count('date'))

    # 循环成功和失败的结果，按照对应的key放在_date_value里面
    _date_value_s = {}
    _date_value_f = {}
    days = []

    for d in range(30):
        day = (end_time + datetime.timedelta(days=(d - 30))).strftime("%Y-%m-%d")
        days.append(day)
        # 初始化
        _date_value_s[day] = 0
        _date_value_f[day] = 0
    # print(days)

    for i in success:
        day = i.get("day").strftime("%Y-%m-%d")
        # print(day)
        value = i.get("number")
        _date_value_s[day] = value

    # print(_date_value_s)
    for i in failed:
        day = i.get("day").strftime("%Y-%m-%d")
        value = i.get("number")
        _date_value_f[day] = value

    # a1 = sorted(_date_value_s.items(), key=lambda x: x[0])

    status = {
        "success": [i for i in _date_value_s.values()],
        "failed": [i for i in _date_value_f.values()],
        "days": days
    }

    return Response(status)
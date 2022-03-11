import datetime

import psutil
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from pyecharts import options as opts
from pyecharts.charts import Gauge
from install.models import Discover, InstallResult, InstallProgress

options_temp = """
{
  tooltip: {
    formatter: '{a} <br/>{b} : {c}%'
  },
  series: [
    {
      name: 'show_name',
      type: 'gauge',
      detail: {
        formatter: '{value}'
      },
      data: [
        {
          value: data_value,
          name: 'data_name'
        }
      ]
    }
  ]
}
"""

def temp(title_name, data_value):
    c = (
        Gauge(init_opts=opts.InitOpts(width="800px", height="800px"))
            .add(
            series_name=title_name,
            data_pair=[("已使用", data_value)],
            radius="50%",
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color=[(0.3, "#67e0e3"), (0.7, "#37a2da"), (1, "#fd666d")], width=15
                )
            ),
            detail_label_opts=opts.GaugeDetailOpts(offset_center=[0, "30%"]),
            title_label_opts=opts.GaugeTitleOpts())
            .set_global_opts(
            title_opts=opts.TitleOpts(title=title_name),
            legend_opts=opts.LegendOpts(is_show=False),
            tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{a} <br/>{b} : {c}%"), )
    )
    return c.dump_options_with_quotes()


def status_temp(title, value, img, link):
    ret = {
          "title": title,
          "value": value,
          "img": img,
          "date": datetime.datetime.now(),
          "link": link
        }
    return ret

# get sys info
# @permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_sys_info(request: Request):
    options = {
        "cpu": temp('CPU使用率', psutil.cpu_percent(interval=1)),
        "disk": temp('硬盘使用率', psutil.virtual_memory().percent),
        "mem": temp('内存使用率', psutil.disk_usage('/').percent)
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
        "client": status_temp('客户端在线数量', client_num, 'https://image.lichunpeng.cn/py_test/ts_client.png', '/discovered'),
        "install": status_temp('正在安装的数量', install_num, 'https://image.lichunpeng.cn/py_test/install.png', '/installing'),
        "success": status_temp('安装成功的数量', success, 'https://image.lichunpeng.cn/py_test/success.png', '/installed'),
        "failed": status_temp('安装失败的数量', failed, 'https://image.lichunpeng.cn/py_test/failed.png', '/installed')
    }
    return Response(status)


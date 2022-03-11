from django.db import models


# Create your models here.

# 发现设备列表
class Discover(models.Model):
    isVM = models.BooleanField(verbose_name="是否为虚拟机")
    sn = models.CharField(blank=False, max_length=20, verbose_name="SN")
    mac = models.CharField(blank=False, max_length=20, verbose_name="MAC地址", primary_key=True)
    vender = models.CharField(blank=True, null=True, max_length=200, verbose_name='厂家')
    product = models.CharField(blank=True, null=True, max_length=200, verbose_name='产品')
    cpuinfo = models.CharField(blank=True, null=True, max_length=200, verbose_name='CPU')
    meminfo = models.CharField(blank=True, null=True, max_length=200, verbose_name='内存')
    status = models.BooleanField(default=True)
    clientip = models.GenericIPAddressField(blank=False, verbose_name="Client IP")
    ipmi = models.GenericIPAddressField(blank=True, null=True, verbose_name="IPMI IP")
    date = models.DateTimeField(blank=False, verbose_name="加入时间", auto_now=True)
    sysinfo = models.JSONField(verbose_name="系统信息")

    class Meta:
        verbose_name = '发现设备列表'
        db_table = 'p_discover_list'
        ordering = ['date']

    def __str__(self):
        return self.sn


# 准备安装列表
class InstallPreList(models.Model):
    isVM = models.BooleanField(verbose_name="是否为虚拟机")
    sn = models.CharField(blank=False, max_length=20, verbose_name="SN")
    mac = models.CharField(blank=False, max_length=20, verbose_name="MAC地址", primary_key=True)
    vender = models.CharField(blank=True, null=True, max_length=200, verbose_name='厂家')
    product = models.CharField(blank=True, null=True, max_length=200, verbose_name='产品')
    os = models.CharField(blank=True, null=True, max_length=100, verbose_name='系统')
    config = models.CharField(blank=True, null=True, max_length=100, verbose_name='配置')
    # status 代表当前状态， 0: 未安装——正在准备， 1: 正在安装
    status = models.BooleanField(default=False)
    clientip = models.GenericIPAddressField(blank=False, verbose_name="Client IP")
    ipmi = models.GenericIPAddressField(blank=True, null=True, verbose_name="IPMI IP")
    pxe_menu_path = models.CharField(blank=True, null=True, max_length=250, verbose_name='启动菜单位置')
    join_date = models.DateTimeField(blank=False, verbose_name="加入时间", auto_now_add=True)
    sysinfo = models.JSONField(verbose_name="系统信息")

    class Meta:
        verbose_name = '发现设备列表'
        db_table = 'p_install_pre_list'
        ordering = ['join_date']

    def __str__(self):
        return self.sn


# 安装进度表
# 先存在redis中？ 等安装完成后，统一写入数据库，建立一个完成表？ 后续做
class InstallProgress(models.Model):
    sn = models.CharField(blank=False, max_length=20, verbose_name="SN")
    mac = models.CharField(blank=False, max_length=20, verbose_name="MAC地址", primary_key=True)
    vender = models.CharField(blank=True, null=True, max_length=200, verbose_name='厂家')
    product = models.CharField(blank=True, null=True, max_length=200, verbose_name='产品')
    os = models.CharField(blank=True, null=True, max_length=100, verbose_name='镜像')
    config = models.CharField(blank=True, null=True, max_length=100, verbose_name='配置')
    clientip = models.GenericIPAddressField(blank=False, verbose_name="Client IP")
    ipmi = models.GenericIPAddressField(blank=True, null=True, verbose_name="IPMI IP")
    install_date = models.DateTimeField(blank=False, verbose_name="安装时间", auto_now_add=True)
    status_id = models.CharField(max_length=20, verbose_name='最新进度状态')
    status_progress = models.CharField(max_length=5, verbose_name='最新进度状态')
    status_content = models.TextField(max_length=10086, verbose_name='所有进度信息')
    pxe_menu_path = models.CharField(blank=True, null=True, max_length=250, verbose_name='启动菜单位置')

    class Meta:
        verbose_name = '安装进度表'
        ordering = ['install_date']
        db_table = 'p_install_progress'


# 结果存储表
# 先存在redis中？ 等安装完成后，统一写入数据库，建立一个完成表？ 后续做
class InstallResult(models.Model):
    sn = models.CharField(blank=False, max_length=20, verbose_name="SN")
    mac = models.CharField(blank=False, max_length=20, verbose_name="MAC地址")
    vender = models.CharField(blank=True, null=True, max_length=200, verbose_name='厂家')
    product = models.CharField(blank=True, null=True, max_length=200, verbose_name='产品')
    os = models.CharField(blank=True, null=True, max_length=100, verbose_name='镜像')
    config = models.CharField(blank=True, null=True, max_length=100, verbose_name='配置')
    clientip = models.GenericIPAddressField(blank=False, verbose_name="Client IP")
    ipmi = models.GenericIPAddressField(blank=True, null=True, verbose_name="IPMI IP")
    date = models.DateTimeField(blank=False, verbose_name="完成时间", auto_now_add=True)
    status = models.BooleanField()
    status_id = models.CharField(max_length=20, verbose_name='最新进度状态')
    status_progress = models.CharField(max_length=5, verbose_name='最新进度状态')
    status_content = models.TextField(max_length=10086, verbose_name='所有进度信息')
    pxe_menu_path = models.CharField(blank=True, null=True, max_length=250, verbose_name='启动菜单位置')

    class Meta:
        verbose_name = '结果存储表'
        db_table = 'p_install_result'
        ordering = ['id']

# 发现设备列表
# class Install(models.Model):
#     sn = models.CharField('SN序列号', max_length=20)
#     mac = models.CharField('MAC地址', max_length=20)
#     info = models.CharField('设备信息', max_length=500)
#     status = models.CharField('当前状态', max_length=20)
#     join_date = models.DateTimeField('加入时间', auto_now_add=True)
#     last_date = models.DateTimeField('修改时间', auto_now=True)
#
#     class Meta:
#         verbose_name = '发现设备列表'
#
#     def __str__(self):
#         return self.sn


# # 安装->设备状态
# class IStatus(models.Model):
#     sn = models.CharField('SN序列号', max_length=20)
#     mac = models.CharField('MAC地址', max_length=20)
#     os_temps = models.CharField('系统模板', max_length=20)
#     hw_temps = models.CharField('硬件模板', max_length=20)
#     ipaddr = models.CharField('设备IP', max_length=100)
#     status = models.CharField('当前状态', max_length=20)
#     vnc = models.CharField('VNC链接', max_length=100)
#
#     class Meta:
#         verbose_name = '安装状态'
#
#     def __str__(self):
#         return self.sn

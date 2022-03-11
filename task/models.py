from django.db import models

# task
# 从发现记录列表转到这里
class TaskList(models.Model):
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
        verbose_name = '任务主机列表'
        db_table = 'p_task_list'
        ordering = ['date']

    def __str__(self):
        return self.sn

# playbook
class PlaybookTemp(models.Model):
    # id
    name = models.CharField(blank=False, max_length=20, verbose_name="模板名称", unique=True)
    content = models.TextField()

    class Meta:
        verbose_name = '任务模板列表'
        db_table = 'p_temp_playbook'
        ordering = ['id']

    def __str__(self):
        return self.name

class TaskResult(models.Model):
    # id
    name = models.CharField(blank=False, max_length=20, verbose_name="主机名称")
    status = models.BooleanField()
    playbook = models.CharField(blank=True, max_length=20, verbose_name="执行模板")
    task_id = models.CharField(blank=True, max_length=200, verbose_name="任务执行ID")
    command = models.CharField(blank=True, max_length=120, verbose_name="执行命令")
    progress = models.IntegerField(blank=True, default=1, verbose_name="任务进度")
    date = models.DateTimeField(blank=False, verbose_name="结束时间", auto_now=True)
    result = models.TextField()

    class Meta:
        verbose_name = '任务结果列表'
        db_table = 'p_task_result'
        ordering = ['date']

    def __str__(self):
        return self.name

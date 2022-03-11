from django.db import models


# 系统镜像
class ImageTemp(models.Model):
    OS_TYPE_CHOICES = [
        ('CentOS', 'CentOS'),
        ('Ubuntu', 'Ubuntu'),
        ('RHEL', 'RHEL'),
        ('Windows', 'Windows'),
    ]
    name = models.CharField(blank=False, max_length=48, verbose_name="镜像名称", unique=True)
    type = models.CharField(blank=False, choices=OS_TYPE_CHOICES, max_length=48, verbose_name="系统类型")
    version = models.CharField(blank=False, max_length=48, verbose_name="系统版本")
    path = models.CharField(blank=False, max_length=250, verbose_name="存储路径")
    save_path = models.CharField(blank=False, max_length=250, verbose_name="实际存储位置")

    class Meta:
        verbose_name = '系统镜像'
        db_table = 'p_temp_image'
        ordering = ['id']

    def __str__(self):
        return self.name


# 系统模板ks
class OSTemp(models.Model):
    # id
    name = models.CharField(blank=False, max_length=20, verbose_name="模板名称", unique=True)
    image = models.ForeignKey(ImageTemp, models.PROTECT, db_column='image_name', to_field='name')
    config = models.TextField()
    path = models.CharField(blank=True, max_length=250, verbose_name="存储路径")
    save_path = models.CharField(blank=True, max_length=250, verbose_name="实际存储位置")

    class Meta:
        verbose_name = '系统模板'
        db_table = 'p_temp_os_config'
        ordering = ['id']

    def __str__(self):
        return self.name




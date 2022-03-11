from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartpxe.settings')

app = Celery('smartpxe')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.broker_url = 'redis://127.0.0.1:6379/0'
app.conf.broker_transport_options = {'visibility_timeout': 43200}
app.conf.result_backend = 'redis://127.0.0.1:6379/1'

app.conf.update(
    enable_utc = True,
    timezone = 'Asia/Shanghai'
)

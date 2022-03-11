from django.db import connections
from django.db.utils import OperationalError
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpRequest


def check_mysql(db_name='default'):
    db_conn = connections[db_name]
    try:
        check = db_conn.cursor()
    except OperationalError:
        return 0
    else:
        return 1


def check_healthy(request: HttpRequest):
    if check_mysql():
        return HttpResponse('ok')
    else:
        return HttpResponse('error')

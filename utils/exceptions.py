from django.http import Http404
from rest_framework import exceptions
from django.core.exceptions import PermissionDenied
from rest_framework.views import set_rollback, Response


class MagBaseException(exceptions.APIException):
    code = "10000"  # 非0都是异常
    message = "非法请求"

    @classmethod
    def get_msg(cls):
        return {'code': cls.code, 'message': cls.message}


class InvalidToken(MagBaseException):  # 405 => 400
    code = 1
    message = "认证已过期，请重新登陆！"


class AuthenticationFailed(MagBaseException):
    code = 2
    message = "用户名或密码无效！"


class NotAuthenticated(MagBaseException):
    code = 3
    message = "未登录，请登陆后重试！"


class ValidationError(MagBaseException):
    code = 101
    message = "后端验证失败，请检查输入信息！"

class InvalidPassword(MagBaseException):
    code = 102
    message = "密码修改失败，请重试！"


# 映射 401 => 400; 403 => 400
exc_map = {
    "InvalidToken": InvalidToken,  # token过期
    "AuthenticationFailed": AuthenticationFailed,  # 密码无效
    "NotAuthenticated": NotAuthenticated,  # 无token登陆
    "ValidationError": ValidationError, # 后端验证失败
    "InvalidPassword": InvalidPassword
}


def exception_handler(exc, context):
    """自己的全局异常处理"""
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    print('~' * 30)
    print(type(exc), exc)
    print('~' * 30)

    if isinstance(exc, exceptions.APIException):
        set_rollback()
        data = exc_map.get(exc.__class__.__name__, MagBaseException).get_msg()
        return Response(data, status=200)

    return None

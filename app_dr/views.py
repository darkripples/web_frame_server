# coding:utf8

from django.http import JsonResponse

from ez_utils.models import ResModel


def index(req):
    """
    2017/05/29 fls
    frist coming
    """
    ret = ResModel()
    ret.msg = '欢迎dr'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())

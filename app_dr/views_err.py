#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/11/30
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   darkripples总平台相关-通用异常func

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/11/30 10:20   fls        1.0         create
"""

from django.http import JsonResponse
from ez_utils.models import ResModel400, ResModel404, ResModel500
from ez_utils import flog


def handler_500(exception, req=None):
    """
    定义异常时的返回值
    > 通过urls.py指定handler500的话，只需exception参数；
    > 通过中间件dr_middleware.py拦截到的异常，会有req信息
    """
    from traceback import format_exc
    flog.error(format_exc())

    # 默认返回值Response
    ret = ResModel500()
    return JsonResponse(ret.to_dic())


def handler_400(request, exception):
    """
    定义400状态的返回值
    """
    ret = ResModel400()
    return JsonResponse(ret.to_dic())


def handler_404(request, exception):
    """
    定义404状态的返回值
    """
    ret = ResModel404()
    return JsonResponse(ret.to_dic())

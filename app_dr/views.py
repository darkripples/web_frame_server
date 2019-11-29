#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/09/02
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   darkripples总平台相关-通用views

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/09/02 11:41   fls        1.0         create
2019/11/22 10:27   fls        1.1         加入djangorestframework-jwt相关，并初始化测试代码
2019/11/29 15:51   fls        2.0         去除测试代码，增加通用文件上传api
"""
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

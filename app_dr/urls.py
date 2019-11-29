#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/09/02
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   darkripples总平台相关

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/09/02 11:41   fls        1.0         create
"""
from django.urls import path
from django.apps import apps

from .views import index

# 不可删除
app_name = apps.get_app_config('app_dr').name

urlpatterns = [
    path(r'index/', index),
]

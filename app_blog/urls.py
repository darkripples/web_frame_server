#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/8/30
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   blog相关

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/8/30 14:53   fls        1.0         create
"""

from django.urls import path

from .views import indexList, contentDetail, typeList, titleValue
from django.apps import apps

# 不可删除
app_name = apps.get_app_config('app_blog').name

urlpatterns = [
    path(r'indexList/', indexList),
    path(r'contentDetail/<str:id>', contentDetail),
    path(r'typeList/', typeList),
    path(r'titleValue/', titleValue),
]

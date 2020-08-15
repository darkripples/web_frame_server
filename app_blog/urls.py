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

from .views import index_list, content_detail, type_list, title_value, save_blog, del_blog
from django.apps import apps

# 不可删除
app_name = apps.get_app_config('app_blog').name

urlpatterns = [
    # 首页列表
    path(r'indexList/', index_list),
    # 详情
    path(r'contentDetail/<str:id>', content_detail),
    # 类型列表
    path(r'typeList/', type_list),
    # 副标题文字
    path(r'titleValue/', title_value),
    # 保存
    path(r'saveObj/<str:mod_type>', save_blog),
    # 删除
    path(r"delObj/<str:blog_id>", del_blog)
]

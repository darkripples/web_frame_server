#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/09/02
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   darkripples总url配置

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/09/02 09:17   fls        1.0         create
"""
from django.urls import path, include

urlpatterns = [
    # 主平台
    path(r'app_dr/', include('app_dr.urls', namespace='app_dr')),
    # blog
    path(r'app_blog/', include('app_blog.urls', namespace='app_blog')),

]

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
2019/11/30 10:10   fls        1.1         增加异常信息的views
"""

from django.urls import path, include

urlpatterns = [
    # 主平台
    path(r'app_dr/', include('app_dr.urls', namespace='app_dr')),
    # blog
    path(r'app_blog/', include('app_blog.urls', namespace='app_blog')),

]

# 其他异常信息
handler400 = "app_dr.views_err.handler_400"
handler404 = "app_dr.views_err.handler_404"
handler500 = "app_dr.views_err.handler_500"

#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/8/30
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   blog相关config

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/8/30 14:53   fls        1.0         create
"""

from django.apps import AppConfig


class AppBlogConfig(AppConfig):
    name = 'app_blog'
    # 定义下述url，将校验token
    check_token_url_list = ('/app_blog/saveObj', '/app_blog/delObj',)

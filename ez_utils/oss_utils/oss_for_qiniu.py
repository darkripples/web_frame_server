#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/10/19
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-对象存储相关utils:七牛oss

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/10/19 10:51   fls        1.0         create
"""

from qiniu import Auth
from conf import QINIU_ACCESS_KEY, QINIU_SECRET_KEY


def get_obj():
    """
    获取qiniu操作对象
    :return:
    """
    return Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)


def get_token(bucket_name, key, vtime=3600):
    """
    获取上传时会话token
    :param bucket_name:
    :param key:
    :param vtime:
    :return:
    """
    q = get_obj()
    return q.upload_token(bucket_name, key, vtime)

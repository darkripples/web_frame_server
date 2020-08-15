# !/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/11/23
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-redis操作相关utils

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/11/23 15:40     fls        1.0         create
"""

import redis
from conf import REDIS_IP, REDIS_PORT, REDIS_PWD


class RedisCtrl:
    """
    redis controller
    """

    def __init__(self, db_num=None):
        """
        创建redis对象
        :param db_num:
        """
        self.robj = redis.Redis(host=REDIS_IP, port=REDIS_PORT, db=(db_num or 0), password=REDIS_PWD)

    def get_one(self, key_str):
        """
        获取元素-单个
        :param key_str:
        :return:
        """
        rs = self.robj.get(key_str)
        return rs.decode('utf8') if rs else None

    def get_more(self, *key_str):
        """
        获取元素-多个
        :param key_str:
        :return:
        """
        return self.robj.mget(*key_str)

    def set_one(self, key_str, v_str, expt=None, nx=None, xx=None):
        """
        保存元素
        :param key_str:
        :param v_str:
        :param expt: 过期时间(秒)
        :param nx: 如果设置为True，则只有name不存在时，当前set操作才执行,同setnx(name, value)
        :param xx: 如果设置为True，则只有name存在时，当前set操作才执行
        :return:
        """
        self.robj.set(key_str, v_str, ex=expt, nx=nx, xx=xx)

    def del_one(self, key_str):
        """
        删除元素
        :param key_str:
        :return:
        """
        return self.robj.delete(key_str)

    def get_ex_time(self, key_str):
        """
        查看元素过期时间-单位:秒
        :param key_str:
        :return:
        """
        return self.robj.ttl(key_str)

# !/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/09/15
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-位置相关utils.ip、经纬度等

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/09/15 16:29     fls        1.0         create
"""

import requests
from functools import reduce


def ip2jwd(ip):
    """
    根据ip地址，获取经纬度
    :param ip:
    :return:
    """
    try:
        url = 'http://api.ipstack.com/{}?access_key=1bdea4d0bf1c3bf35c4ba9456a357ce3'.format(ip)
        response = requests.get(url)
        js = response.json()
        lat = js['latitude']
        lon = js['longitude']
    except:
        return ['', '']
    return [lat, lon]


def ip_into_int(ip):
    # 先把 192.168.1.13 变成16进制的 c0.a8.01.0d ，再去了“.”后转成10进制的 3232235789 即可。
    # (((((192 * 256) + 168) * 256) + 1) * 256) + 13
    return reduce(lambda x, y: (x << 8) + y, map(int, ip.split('.')))


def is_internal_ip(ip):
    """
    判断是否为内网ip
    :param ip:
    :return:
    """
    if ip in ('127.0.0.1', '0.0.0.0', 'localhost'):
        return True
    ip = ip_into_int(ip)
    net_a = ip_into_int('10.255.255.255') >> 24
    net_b = ip_into_int('172.31.255.255') >> 20
    net_c = ip_into_int('192.168.255.255') >> 16
    return ip >> 24 == net_a or ip >> 20 == net_b or ip >> 16 == net_c

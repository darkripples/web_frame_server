#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/09/15
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   darkripples总平台相关-应用内utils

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/09/15 08:43   fls        1.0         create
"""

import re
import uuid

from django.conf import settings
from django.utils import timezone

from conf import REQ_HEADER_PWD
from ez_utils import connection, after_seconds, is_internal_ip, get_ip, fls_log
from .models import SQL_DIC_VISITOR, DrVisitorInfo

flog = fls_log(handler_name="app_dr.dr_utils")


def add_visitor(ip, app_type, visitor_type, link_id):
    """
    添加到访客记录
    :param ip: 同ip，5分钟内，只记录一次
    :param app_type:
    :param visitor_type:
    :param link_id: 关联的id，可以不关联到业务表，用于记录访客随便输入的id
    :return:
    """
    with connection() as con:
        rs = con.execute_sql(
            "SELECT count(1) as cnt FROM {table1} " \
            "WHERE {table1_ip} = %(ip)s and {table1_atime}>=%(time)s and {table1_linkid}=%(link_id)s".format(
                **SQL_DIC_VISITOR), {'ip': ip, 'time': after_seconds(seconds=-1 * 5 * 60), 'link_id': link_id})
        if not rs or rs[0].cnt == 0:
            # 若登记过该ip，则获取它的信息
            cnt_ipstack = 0
            visitor_lat = ''
            visitor_lng = ''
            if is_internal_ip(ip) or '127.0.0.1' == ip:
                # 内网ip，免解析
                cnt_ipstack = -1
            else:
                rs_over = con.execute_sql(
                    "SELECT {table1_lat},{table1_lng} FROM {table1} " \
                    "WHERE {table1_ip} = %(ip)s and {table1_lat} is not null and {table1_lat}!='' limit 1".format(
                        **SQL_DIC_VISITOR), {'ip': ip}, hump=False)

                if rs_over and rs_over[0]:
                    cnt_ipstack = -1
                    visitor_lat = rs_over[0][SQL_DIC_VISITOR["table1_lat"]]
                    visitor_lng = rs_over[0][SQL_DIC_VISITOR["table1_lng"]]

            # 登记信息
            DrVisitorInfo.objects.create(id=str(uuid.uuid1()).replace('-', ''), visitor_ip=ip,
                                         add_time=timezone.now(), app_name=app_type,
                                         visitor_type=visitor_type, link_id=link_id,
                                         cnt_ipstack=cnt_ipstack, visitor_lat=visitor_lat,
                                         visitor_lng=visitor_lng)

            return 1
    return 0


def req_invalid_check(req):
    """
    request合法性校验
    :param req:
    :return: 校验通过return ''，否则return错误信息
    """
    flag = ""
    if req.META.get("HTTP_DR_DEBUG") == REQ_HEADER_PWD:
        # 测试时，传递该密参，不进行校验
        return flag

    # 其他情况，校验header中的参数
    ip = get_ip(req)
    if req.META.get("HTTP_TOKEN") is None:
        flag = 1

    allowed_hosts = settings.ALLOWED_HOSTS

    referer_rule = r'//(.*?)/'
    referer_rs = re.findall(referer_rule, req.META.get("HTTP_REFERER", ""))
    if (not referer_rs) or (referer_rs[0] not in allowed_hosts):
        flag = 1
    # origin_rs = req.META.get("HTTP_ORIGIN", "").split("//")
    # if (len(origin_rs) < 2) or (origin_rs[1] not in allowed_hosts):
    #     flag = 1

    if flag:
        flag = f"当前客户端外网IP:{ip}.请斟酌调取本接口"
    return flag

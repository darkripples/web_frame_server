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

from re import findall
from uuid import uuid1
from json import dumps, loads

from django.conf import settings
from django.utils import timezone

from conf import REQ_HEADER_PWD, REDIS_KEY_PRE_TOKEN
from ez_utils import connection, after_seconds, is_internal_ip, get_ip, flog, RedisCtrl, ParamsVerifyError
from .models import SQL_DIC_VISITOR, DrVisitorInfo


def add_visitor(ip, app_type, visitor_type, link_id, bz=None):
    """
    添加到访客记录
    :param ip: 同ip，5分钟内，只记录一次
    :param app_type:
    :param visitor_type:
    :param link_id: 关联的id，可以不关联到业务表，用于记录访客随便输入的id
    :param bz:备注
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
            cnt_iptaobao = 0
            visitor_lat = ''
            visitor_lng = ''
            visitor_city = ''
            visitor_addr = ''
            visitor_isp = ''
            if is_internal_ip(ip):
                # 内网ip，免解析
                cnt_ipstack = -1
            else:
                rs_over = con.execute_sql(
                    """SELECT {table1_lat},{table1_lng},{table1_city},{table1_addr},{table1_isp} FROM {table1} 
                    WHERE {table1_ip} = %(ip)s 
                        and (
                            {table1_ipstack}=-1 or {table1_iptaobao}=-1
                        ) limit 1""".format(**SQL_DIC_VISITOR), {'ip': ip}, hump=False)

                if rs_over and rs_over[0]:
                    cnt_ipstack = -1
                    cnt_iptaobao = -1
                    visitor_lat = rs_over[0][SQL_DIC_VISITOR["table1_lat"]]
                    visitor_lng = rs_over[0][SQL_DIC_VISITOR["table1_lng"]]
                    visitor_city = rs_over[0][SQL_DIC_VISITOR["table1_city"]]
                    visitor_addr = rs_over[0][SQL_DIC_VISITOR["table1_addr"]]
                    visitor_isp = rs_over[0][SQL_DIC_VISITOR["table1_isp"]]

            # 登记信息
            DrVisitorInfo.objects.create(id=str(uuid1()).replace('-', ''), visitor_ip=ip,
                                         add_time=timezone.now(), app_name=app_type,
                                         visitor_type=visitor_type, link_id=link_id,
                                         cnt_ipstack=cnt_ipstack, visitor_lat=visitor_lat,
                                         visitor_lng=visitor_lng, visitor_city=visitor_city,
                                         visitor_addr=visitor_addr, visitor_isp=visitor_isp,
                                         cnt_iptaobao=cnt_iptaobao, bz=bz)

            return 1
    return 0


def req_invalid_check(req):
    """
    request合法性校验
    :param req:
    :return: 校验通过return ''，否则return错误信息
    """
    flag = ""
    ip = get_ip(req)
    # ... 省略
    if flag:
        flag = f"当前客户端外网IP:{ip}.请斟酌调取本接口"
    return flag


def create_token(user_info: dict, expt=None):
    """
    生成token
    :param user_info: 必须为json字典，尽量简短
    :param expt: 过期时间(秒)
    :return:
    """
    if user_info.get("id"):
        r = RedisCtrl()
        token = str(uuid1()).replace('-', '')
        if not expt:
            # 3小时
            expt = 60 * 3600 * 3
        elif expt == -1:
            expt = None
        r.set_one(REDIS_KEY_PRE_TOKEN + token, dumps(user_info), expt=expt)
        return token
    else:
        raise ParamsVerifyError("生成用户token需有`id`作为必填key")


def check_token(req_token):
    """
    校验token
    :param req_token:
    :return:
    """
    user_info = {}
    ret_info = None
    if not req_token:
        ret_info = "请登录后访问"
        return ret_info, user_info
    r = RedisCtrl()
    user_info = r.get_one(REDIS_KEY_PRE_TOKEN + req_token)
    if user_info:
        user_info = loads(user_info)
    else:
        ret_info = "无效的token"
    return ret_info, user_info


def upd_token_exp(req_token, expt=None):
    """
    更新token过期时间
    :param req_token:
    :param expt: 过期时间(秒)
    :return:
    """
    r = RedisCtrl()
    user_info = r.get_one(REDIS_KEY_PRE_TOKEN + req_token)
    if user_info:
        if not expt:
            # 3小时
            expt = 60 * 3600 * 3
        r.set_one(REDIS_KEY_PRE_TOKEN + req_token, user_info, expt=expt)

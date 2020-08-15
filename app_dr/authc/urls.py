#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/11/26
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   darkripples总平台相关-用户及权限相关

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/11/26 08:52   fls        1.0         create
"""

from django.urls import path
from .views_log_in import sms_log_in, vcode_sid, log_in, sid_pic, log_in_openid
from .views_reg import sms_reg, email_reg, user_reg, user_reg_openid

app_name = 'app_dr_authc'

urlpatterns = [
    path(r'vcodeSid/', vcode_sid),
    path(r'sid2pic/<str:sid>', sid_pic),
    path(r'smsLogin/<str:sid>/<str:vcode>', sms_log_in),
    path(r'login/<str:code_way>/<str:sid>', log_in),
    # 根据openid登录,token不失效
    path(r'loginOId/<str:yw_name>/<str:openid>', log_in_openid),
    # register
    path(r'smsReg/<str:sid>/<str:vcode>', sms_reg),
    path(r'emailReg/<str:sid>/<str:vcode>', email_reg),
    path(r'userReg/', user_reg),
    # 根据openid注册，email和phone不必填;但是填写email没事，若填写phone，则需有短信校验auth_code
    path(r'userRegOId/<str:yw_name>/<str:openid>', user_reg_openid),
]

#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/11/26
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   darkripples总平台相关-用户相关

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/11/26 08:52   fls        1.0         create
"""

from django.urls import path
from .views_user import (log_out, get_info, modify_info, modify_pwd, sms_reset_pwd, email_reset_pwd, reset_pwd,
                         sms_reset_phone, email_reset_email, reset_phone_email, get_list as user_get_list)
from .views_role import get_list as role_get_list, save_obj as role_save_obj, del_obj as role_del_obj

app_name = 'app_dr_user'

urlpatterns = [
    # 登出
    path(r'logout/', log_out),
    # 查询信息
    path(r'getInfo/', get_info),
    # 修改信息
    path(r'modInfo/', modify_info),
    # 修改密码，通过原密码
    path(r'modPwd/', modify_pwd),
    # 重置密码，通过手机号验证码、email验证码
    path(r'smsSetPwd/<str:sid>/<str:vcode>', sms_reset_pwd),
    path(r'emailSetPwd/<str:sid>/<str:vcode>', email_reset_pwd),
    # 重置密码-提交
    path(r'resetPwd/<str:code_way>/<str:sid>', reset_pwd),
    # 修改或绑定phone，通过新phone短信验证码
    path(r'smsSetPhone/<str:sid>/<str:vcode>', sms_reset_phone),
    # 修改或绑定email，通过新email验证码
    path(r'emailSetEmail/<str:sid>/<str:vcode>', email_reset_email),
    # 修改或绑定手机号、email-提交
    path(r'resetPhoneEmail/<str:code_way>/<str:sid>', reset_phone_email),

    # 用户列表
    path(r'list/', user_get_list),
    # 角色列表
    path(r'role/list/', role_get_list),
    # 保存角色信息
    path(r'role/save/', role_save_obj),
    # 删除角色信息
    path(r'role/del/', role_del_obj),

]

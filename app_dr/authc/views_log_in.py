#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/11/26
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   darkripples总平台相关-用户及权限相关:用户登录

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/11/26 08:52   fls        1.0         create
2020/08/14 17:53   fls        1.1         登录接口调优
"""

from uuid import uuid1
from random import randint
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from django.conf import settings
from ez_utils.models import ResModel
from ez_utils import RedisCtrl, ValidCodeImg, connection, flog, get_ip, PwdCtrl, sms_send
from app_dr.dr_utils import add_visitor, req_invalid_check, create_token
from conf import (ALI_SMS_TMPL_COMMON_CODE, REDIS_KEY_PRE_SID, REDIS_KEY_PRE_SMSCODE,
                  REDIS_KEY_PRE_CODEERR, REDIS_KEY_PRE_SIDERR, MINI_PROGRAM_APP_CONF)
from app_dr.user.models import SQL_DIC_USER, SQL_DIC_USEROPENID, SQL_DIC_ROLES, SQL_DIC_USERROLE


@csrf_exempt
@require_POST
def vcode_sid(req):
    """
    验证码-获取sid
    生成sid及验证码字符串,有效期10分钟
    :param req:
    :return:
    """
    ret = ResModel()
    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        return JsonResponse(ret.to_dic())

    r = RedisCtrl()
    ret.data = str(uuid1()).replace("-", "").lower()
    r.set_one(REDIS_KEY_PRE_SID + ret.data, ValidCodeImg.getRandomStr(5), expt=60 * 10)
    ret.msg = ''
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@csrf_exempt
@require_POST
def sid_pic(req, sid):
    """
    验证码-根据sid生成图片
    :param req:
    :return:
    """
    ret = ResModel()
    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        return JsonResponse(ret.to_dic())
    r = RedisCtrl()
    verify_code = r.get_one(REDIS_KEY_PRE_SID + sid)
    if not verify_code:
        # 正常情况下get_sid和本函数是无间隔顺序调用的，所以不会出现redis中不存在的情况，不必友好提示
        return JsonResponse(ret.to_dic())

    # 生成验证码图片.
    i = ValidCodeImg(code_count=5, img_format='png')
    img_data, valid_str = i.getValidCodeImg(vcode_str=verify_code)
    ret.data = img_data.decode('utf8')
    ret.msg = ''
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@csrf_exempt
@require_POST
def sms_log_in(req, sid, vcode):
    """
    登录-短信验证码发送
    短信验证码有效期5分钟
    :param req:
    :param sid:
    :param vcode:
    :return:
    """
    ret = ResModel()
    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        return JsonResponse(ret.to_dic())
    phone = req.POST.get('phone', '')
    if not phone:
        ret.msg = '参数异常'
        return JsonResponse(ret.to_dic())

    # 校验
    r = RedisCtrl()
    verify_code = r.get_one(REDIS_KEY_PRE_SID + sid)
    if not verify_code:
        ret.msg = '验证码已过期'
        return JsonResponse(ret.to_dic())
    if verify_code.upper() != vcode.upper():
        ret.msg = '验证码错误'
        # 记录错误次数，多次失败则需重新请求sid
        err_cnt = r.get_one(REDIS_KEY_PRE_SIDERR + sid)
        if not err_cnt:
            err_cnt = 1
            r.set_one(REDIS_KEY_PRE_SIDERR + sid, str(err_cnt), expt=60 * 5)
        else:
            err_cnt = int(err_cnt) + 1
            r.set_one(REDIS_KEY_PRE_SIDERR + sid, str(err_cnt), expt=60 * 5)
        if int(err_cnt) >= 10:
            # 尝试次数大于10次，则需重新请求sid
            r.del_one(REDIS_KEY_PRE_SID + sid)
            r.del_one(REDIS_KEY_PRE_SIDERR + sid)
        return JsonResponse(ret.to_dic())

    # 校验用户是否存在
    with connection() as con:
        user_rs = con.execute_sql(
            """select {table1_id}, {table1_uname}, {table1_pwd}, {table1_salt}, 
                {table1_wx}, {table1_qq}, {table1_phone}, {table1_email} 
            from {table1} 
            where {table1_phone}=%(phone)s """.format(**SQL_DIC_USER), {"phone": phone}
        )
        if (not user_rs) or (not user_rs[0]):
            ret.msg = '当前用户信息不存在'
            return JsonResponse(ret.to_dic())

    # 短信验证码发送
    sms_code = "%06d" % randint(0, 999999)
    r.set_one(REDIS_KEY_PRE_SMSCODE + phone, sms_code, expt=60 * 5)
    sms_ret = sms_send(phone, {"code": sms_code}, ALI_SMS_TMPL_COMMON_CODE, "登录验证码")
    flog.debug(f"登录验证码发送:{sms_ret}")

    ret.msg = '已发送'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@csrf_exempt
@require_POST
def log_in(req, code_way, sid):
    """
    log_in
    :param req:
    :param code_way: smscode.短信验证码;piccode.图形验证码
    :param sid: 验证码会话sid
    :return:
    """
    ret = ResModel()
    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        return JsonResponse(ret.to_dic())

    # 获取redis缓存数据
    r = RedisCtrl()
    verify_code = r.get_one(REDIS_KEY_PRE_SID + sid)
    if not verify_code:
        ret.msg = '验证码已过期'
        return JsonResponse(ret.to_dic())

    # 图形验证码or短信验证码
    auth_code = req.POST.get('authCode', '').upper()
    # 用户账户,若为短信方式，则该字段为手机号；图形验证码的话，该字段可以是account、email、phone
    user_acc = req.POST.get('userAcc', '')
    # 密码为为md5加密的值
    pwd = req.POST.get('pwd', '').upper()
    # 是否需校验密码
    need_check_pwd = False

    if code_way == 'piccode':
        # 登录方式.piccode.图形验证码
        # 校验验证码
        if (not settings.DEBUG) and (verify_code.upper() != auth_code):
            # 是否为debug模式,非debug模式，需校验验证码
            ret.msg = '验证码错误'
            return JsonResponse(ret.to_dic())
        need_check_pwd = True
    elif code_way == 'smscode':
        # 登录方式.smscode.短信验证码
        sms_code = r.get_one(REDIS_KEY_PRE_SMSCODE + user_acc)
        if not sms_code:
            # 短信验证码不存在
            ret.msg = '验证码已过期'
            return JsonResponse(ret.to_dic())
        if (not settings.DEBUG) and (sms_code != auth_code):
            # 是否为debug模式,非debug模式，需校验验证码
            ret.msg = '短信验证码错误'
            # 记录错误次数，多次失败则需重新请求sid
            err_cnt = r.get_one(REDIS_KEY_PRE_CODEERR + user_acc)
            if not err_cnt:
                err_cnt = 1
                r.set_one(REDIS_KEY_PRE_CODEERR + user_acc, str(err_cnt), expt=60 * 5)
            else:
                err_cnt = int(err_cnt) + 1
                r.set_one(REDIS_KEY_PRE_CODEERR + user_acc, str(err_cnt), expt=60 * 5)
            if int(err_cnt) >= 10:
                # 尝试次数大于10次，则需重新发送sms
                r.del_one(REDIS_KEY_PRE_SMSCODE + user_acc)
                r.del_one(REDIS_KEY_PRE_CODEERR + user_acc)
                # 同一个手机号验证码尝试次数过多
                flog.warning(f"短信验证码登录时[{user_acc}]用户的短信验证码尝试次数过多")
                ret.msg = '短信验证码错误，请重新加载'
            return JsonResponse(ret.to_dic())
    else:
        # 其他code_way,反馈失败
        return JsonResponse(ret.to_dic())

    # 查询用户信息
    with connection() as con:
        user_rs = con.execute_sql(
            """select {table1_id}, {table1_account}, {table1_uname}, {table1_pwd}, {table1_salt},
            {table1_wx}, {table1_qq}, {table1_phone}, {table1_email} 
            from {table1} 
            where ( {table1_account}=%(user_acc)s or {table1_phone}=%(user_acc)s or {table1_email}=%(user_acc)s)""".format(
                **SQL_DIC_USER),
            {"user_acc": user_acc}
        )
        if user_rs and user_rs[0]:
            user_obj = user_rs[0]
            # 获取用户角色
            role_rs = con.execute_sql(
                """select a.{tabler_id} as id from {tabler} a, {table3} b 
                where a.{tabler_id}=b.{table3_rid}
                    and b.{table3_uid}=%(uid)s""".format(**{**SQL_DIC_ROLES, **SQL_DIC_USERROLE}),
                {"uid": user_obj.id})
            roles = ','.join([i.id for i in role_rs])
        else:
            # 需校验密码的话，提示语要隐晦一些
            ret.msg = '用户名或密码错误' if need_check_pwd else '用户信息不存在'
            return JsonResponse(ret.to_dic())

    if need_check_pwd:
        # 接下来校验account-pwd 或 phone-pwd 或 email-pwd
        db_pwd = user_obj.pwdValue or ''
        db_salt = user_obj.pwdSalt
        # 密码校验
        p = PwdCtrl()
        if db_pwd.upper() != p.create_md5(src_str=pwd, salt=db_salt):
            # 密码校验不通过
            ret.msg = '用户名或密码错误'
            return JsonResponse(ret.to_dic())

    # 记录登录日志
    add_visitor(get_ip(req), apps.get_app_config('app_dr').name, 'login', user_obj.id)

    # 组织可见的user_info
    user_info = {"id": user_obj.id, "username": user_obj.userName, "account": user_obj.account}

    # 生成登录token
    # redis中额外放入元素roles等；但是不必返回前端
    user_info_redis = {**user_info}
    user_info_redis["roles"] = roles
    token = create_token(user_info_redis)
    ret.data = {"token": token, "referer": req.META.get("HTTP_REFERER"), "userInfo": user_info}

    ret.msg = f'欢迎{user_obj.userName}'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@csrf_exempt
@require_POST
def log_in_openid(req, yw_name, openid):
    """
    根据openid登录
        1.查询redis是否存在该openid用户:
            1.1.存在则直接return
            1.2.不存在则查询db:
                a.获取用户信息存入redis后return
                b.无用户信息则return空，可走注册流程
    :param req:
    :param yw_name:
    :param openid:
    :return:
    """
    ret = ResModel()

    app_idsecret = MINI_PROGRAM_APP_CONF.get(yw_name)
    if not app_idsecret:
        ret.msg = '未配置的应用名称'
        return JsonResponse(ret.to_dic())

    ret.msg = ''
    ret.code = ret.ResCode.succ

    app_id, app_secret = app_idsecret

    user_obj = None
    r = RedisCtrl()
    token = r.get_one(app_id + openid)
    if token:
        user_obj = r.get_one(token)
    else:
        with connection() as con:
            sql = """select a.{table1_id}, a.{table1_uname}, a.{table1_pwd}, a.{table1_salt},
            a.{table1_wx}, a.{table1_qq}, a.{table1_phone}, a.{table1_email} 
            from {table1} a, {tableo} b
            where a.{table1_id}=b.{tableo_uid} 
                and b.{tableo_aid}=%(appid)s 
                and b.{tableo_oid}=%(oid)s 
            """.format(**{**SQL_DIC_USER, **SQL_DIC_USEROPENID})
            user_rs = con.execute_sql(sql, {"appid": app_id, "oid": openid})
            if user_rs and user_rs[0]:
                user_obj = user_rs[0]
            else:
                ret.msg = '用户信息不存在'

    if user_obj:
        # 记录登录日志
        add_visitor(get_ip(req), apps.get_app_config('app_mf').name, 'login', user_obj.id)

        # 组织可见的user_info
        user_info = {"id": user_obj.id, "username": user_obj.userName}

        # 生成登录token
        # 存入缓存格式:   token:user_info
        token_tmp = create_token(user_info, expt=-1)
        # 存入缓存格式:   appid+openid:token
        r.set_one(app_id + openid, token_tmp)

        ret.data = {"token": token_tmp, "userInfo": user_info}
    else:
        ret.data = {}
    return JsonResponse(ret.to_dic())

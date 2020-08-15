#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/11/26
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   darkripples总平台相关-用户及权限相关:用户注册

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/11/26 08:52   fls        1.0         create
"""

from random import randint
from uuid import uuid1
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from ez_utils import RedisCtrl, connection, sms_send, email_send, PwdCtrl, fmt_date, flog, FMT_DATETIME
from ez_utils.models import ResModel
from app_dr.dr_utils import req_invalid_check
from conf import (ALI_SMS_TMPL_COMMON_CODE, REDIS_KEY_PRE_SID, REDIS_KEY_PRE_SIDERR, REDIS_KEY_PRE_SMSCODE,
                  REDIS_KEY_PRE_EMAILCODE, EMAIL_REG_TITLE, EMAIL_REG_CONT_CODE, REDIS_KEY_PRE_CODEERR,
                  MINI_PROGRAM_APP_CONF)

from app_dr.user.models import (SQL_DIC_USER, SQL_DIC_USERROLE, DrRoles, SQL_DIC_USERINFO, DrUserInfo, DrUser,
                                SQL_DIC_USEROPENID)


@csrf_exempt
@require_POST
def sms_reg(req, sid, vcode):
    """
    注册-短信验证码发送
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
    user_acc = req.POST.get('userAcc', '')
    if not user_acc:
        ret.msg = '参数错误'
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
            """select {table1_id} from {table1} where {table1_account}=%(acc)s """.format(**SQL_DIC_USER),
            {"acc": user_acc}
        )
        if user_rs:
            ret.msg = '当前用户账户已存在'
            return JsonResponse(ret.to_dic())

        user_rs = con.execute_sql(
            """select {table1_id} from {table1} where {table1_phone}=%(phone)s """.format(**SQL_DIC_USER),
            {"phone": phone}
        )
        if user_rs:
            ret.msg = '该手机号用户已存在'
            return JsonResponse(ret.to_dic())

    # 短信验证码发送
    sms_code = "%06d" % randint(0, 999999)
    r.set_one(REDIS_KEY_PRE_SMSCODE + phone, sms_code, expt=60 * 5)
    sms_send(phone, {"code": sms_code}, ALI_SMS_TMPL_COMMON_CODE, "注册验证码")

    ret.msg = '已发送'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@csrf_exempt
@require_POST
def email_reg(req, sid, vcode):
    """
    注册-邮件验证码发送
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
    email = req.POST.get('email', '')
    if not email:
        ret.msg = '参数异常'
        return JsonResponse(ret.to_dic())
    user_acc = req.POST.get('userAcc', '')
    if not user_acc:
        ret.msg = '参数错误'
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
            """select {table1_id} from {table1} where {table1_account}=%(acc)s """.format(**SQL_DIC_USER),
            {"acc": user_acc}
        )
        if user_rs:
            ret.msg = '当前用户账户已存在'
            return JsonResponse(ret.to_dic())

        user_rs = con.execute_sql(
            """select {table1_id} from {table1} where {table1_email}=%(email)s """.format(**SQL_DIC_USER),
            {"email": email}
        )
        if user_rs:
            ret.msg = '该邮箱用户已存在'
            return JsonResponse(ret.to_dic())

    # email验证码发送
    email_code = "%06d" % randint(0, 999999)
    r.set_one(REDIS_KEY_PRE_EMAILCODE + email, email_code, expt=60 * 6)
    send_ret = email_send([email], EMAIL_REG_TITLE, EMAIL_REG_CONT_CODE % email_code)
    flog.error(email + f"注册时发送email验证码err:{send_ret}")

    ret.msg = '已发送'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@csrf_exempt
@require_POST
def user_reg(req):
    """
    register
    :param req: 非空：userAcc,userName,authCode,pwd
                必选：phone/email,
    :return:
    """
    ret = ResModel()
    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        return JsonResponse(ret.to_dic())

    # 必填
    user_acc = req.POST.get('userAcc', '')
    if not user_acc:
        ret.msg = '参数错误'
        return JsonResponse(ret.to_dic())
    # 二选一，若同时填写，则email状态需为待验证
    phone = req.POST.get('phone')
    email = req.POST.get('email')
    # 验证码
    auth_code = req.POST.get('authCode', '').upper().strip()
    if not auth_code:
        ret.msg = '注册码错误'
        return JsonResponse(ret.to_dic())
    # 用户名
    user_name = req.POST.get('userName', user_acc)
    # password
    pwd_value = req.POST.get('pwd', '').upper()
    # 校验验证码
    r = RedisCtrl()
    if phone:
        verify_code = r.get_one(REDIS_KEY_PRE_SMSCODE + phone)
        sub_sql = " {table1_phone}=%(code_phone)s "
    elif email:
        verify_code = r.get_one(REDIS_KEY_PRE_EMAILCODE + email)
        sub_sql = " {table1_email}=%(code_email)s "
    else:
        ret.msg = '参数错误'
        return JsonResponse(ret.to_dic())

    # 校验auth_code
    if not verify_code:
        ret.msg = '注册码错误'
        return JsonResponse(ret.to_dic())
    if verify_code.upper() != auth_code:
        ret.msg = '注册码错误'
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
            flog.warning(f"注册操作[{user_acc}]用户的验证码尝试次数过多")
            ret.msg = '注册码错误，请重新加载'
        return JsonResponse(ret.to_dic())

    # 校验用户是否存在
    sql = "select {table1_id} from {table1} where ({table1_account}=%(acc)s or " + sub_sql + ")"
    with connection() as con:
        user_rs = con.execute_sql(sql.format(**SQL_DIC_USER),
                                  {"code_phone": phone, "code_email": email, "acc": user_acc})
        if user_rs:
            ret.msg = '当前用户已存在'
            return JsonResponse(ret.to_dic())

    # 登记用户信息
    p = PwdCtrl()
    salt = p.get_salt()
    pwd = p.create_md5(src_str=pwd_value, salt=salt)
    now_date = fmt_date()
    with connection() as con:
        # 开启事务
        uid = str(uuid1()).replace('-', '')
        # insert用户表
        email_succ = DrUser.EMAIL_SUCC[0][0]
        if phone:
            # 手机号存在，则说明是phone方式注册；此时email字段可能填写了也可能未填写，但都是`未验证`状态
            email_succ = DrUser.EMAIL_SUCC[1][0]
        sql_ins1 = """insert into {table1}({table1_id}, {table1_account}, {table1_uname}, 
                        {table1_pwd}, {table1_salt}, {table1_phone}, {table1_email},
                        {table1_atime}, {table1_utime}, {table1_emailsucc}) 
                    values(%(id)s,%(acc)s,%(name)s,
                        %(pwd)s,%(salt)s,%(phone)s,%(email)s,
                        %(atime)s,%(utime)s, %(email_succ)s)"""
        con.execute_sql(sql_ins1.format(**SQL_DIC_USER), {"id": uid, "acc": user_acc, "name": user_name,
                                                          "pwd": pwd, "salt": salt, "phone": phone, "email": email,
                                                          "atime": now_date, "utime": now_date,
                                                          "email_succ": email_succ})
        # insert用户详情
        sql_ins11 = """insert into {table11}({table11_id},{table11_atime}, {table11_utime},{table11_sex}) 
                    values(%(id)s,%(atime)s,%(utime)s,%(sex)s)"""
        con.execute_sql(sql_ins11.format(**SQL_DIC_USERINFO),
                        {"id": uid, "atime": now_date, "utime": now_date, "sex": DrUserInfo.SEX_TYPE[0][0]})
        # insert角色信息
        sql_ins2 = """insert into {table3}({table3_id}, {table3_uid}, {table3_rid}) 
                    values(%(id)s, %(uid)s, %(rid)s)"""
        con.execute_sql(sql_ins2.format(**SQL_DIC_USERROLE), {"id": str(uuid1()).replace('-', ''),
                                                              "uid": uid, "rid": DrRoles.type_user})
    ret.msg = '注册成功'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@csrf_exempt
@require_POST
def user_reg_openid(req, yw_name, openid):
    """
    register for openid
    :param req: 非空：userAcc,userName,authCode,pwd
                可选：email,
                不可填写phone
    :param yw_name:
    :param openid:
    :return:
    """
    ret = ResModel()

    app_idsecret = MINI_PROGRAM_APP_CONF.get(yw_name)
    if not app_idsecret:
        ret.msg = '未配置的应用名称'
        return JsonResponse(ret.to_dic())

    app_id, app_secret = app_idsecret

    # 必填.此模式下,用时间戳+随机数代入
    user_acc = fmt_date(fmt=FMT_DATETIME) + "%06d" % randint(0, 999999)
    # 二选一，若同时填写，则email状态需为待验证
    phone = req.POST.get('phone')
    email = req.POST.get('email')
    # 验证码
    auth_code = req.POST.get('authCode', '').upper().strip()
    if phone and (not auth_code):
        ret.msg = '注册码错误'
        return JsonResponse(ret.to_dic())
    # 用户名
    user_name = req.POST.get('userName', user_acc)
    # password 默认值 todo
    pwd_value = req.POST.get('pwd', '123456').upper()
    sex_type = req.POST.get('sexType', DrUserInfo.SEX_TYPE[0][0])
    user_p = req.POST.get('userP')
    user_c = req.POST.get('userC')
    user_a = req.POST.get('userA')
    user_local = req.POST.get('userLocation')
    # 校验验证码
    r = RedisCtrl()
    if phone:
        verify_code = r.get_one(REDIS_KEY_PRE_SMSCODE + phone)

        # 校验auth_code
        if not verify_code:
            ret.msg = '注册码错误'
            return JsonResponse(ret.to_dic())

        if verify_code.upper() != auth_code:
            ret.msg = '注册码错误'
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
                flog.warning(f"注册操作[{user_acc}]用户的验证码尝试次数过多")
                ret.msg = '注册码错误，请重新加载'
            return JsonResponse(ret.to_dic())

    # 校验用户是否存在
    sql = "select {tableo_uid} from {tableo} where {tableo_aid}=%(aid)s and {tableo_oid}=%(oid)s"
    with connection() as con:
        user_rs = con.execute_sql(sql.format(**SQL_DIC_USEROPENID), {"aid": app_id, "oid": openid})
        if user_rs:
            ret.msg = '当前用户已存在'
            return JsonResponse(ret.to_dic())

    # 登记用户信息
    p = PwdCtrl()
    salt = p.get_salt()
    pwd = p.create_md5(src_str=pwd_value, salt=salt)
    now_date = fmt_date()
    with connection() as con:
        # 开启事务
        uid = str(uuid1()).replace('-', '')
        # insert用户表
        email_succ = DrUser.EMAIL_SUCC[0][0]
        if phone:
            # 手机号存在，则说明是phone方式注册；此时email字段可能填写了也可能未填写，但都是`未验证`状态
            email_succ = DrUser.EMAIL_SUCC[1][0]
        sql_ins1 = """insert into {table1}({table1_id}, {table1_account}, {table1_uname}, 
                        {table1_pwd}, {table1_salt}, {table1_phone}, {table1_email},
                        {table1_atime}, {table1_utime}, {table1_emailsucc}) 
                    values(%(id)s,%(acc)s,%(name)s,
                        %(pwd)s,%(salt)s,%(phone)s,%(email)s,
                        %(atime)s,%(utime)s, %(email_succ)s)"""
        con.execute_sql(sql_ins1.format(**SQL_DIC_USER), {"id": uid, "acc": user_acc, "name": user_name,
                                                          "pwd": pwd, "salt": salt, "phone": phone, "email": email,
                                                          "atime": now_date, "utime": now_date,
                                                          "email_succ": email_succ})
        # insert用户详情
        sql_ins11 = """insert into {table11}({table11_id},{table11_atime}, {table11_utime},{table11_sex},
                        {table11_p},{table11_c},{table11_a},{table11_local}) 
                    values(%(id)s,%(atime)s,%(utime)s,%(sex)s,
                        %(uP)s, %(uC)s, %(uA)s, %(uL)s)"""
        con.execute_sql(sql_ins11.format(**SQL_DIC_USERINFO),
                        {"id": uid, "atime": now_date, "utime": now_date, "sex": sex_type,
                         "uP": user_p, "uC": user_c, "uA": user_a, "uL": user_local, })
        # insert角色信息
        sql_ins2 = """insert into {table3}({table3_id}, {table3_uid}, {table3_rid}) 
                    values(%(id)s, %(uid)s, %(rid)s)"""
        con.execute_sql(sql_ins2.format(**SQL_DIC_USERROLE), {"id": str(uuid1()).replace('-', ''),
                                                              "uid": uid, "rid": DrRoles.type_user})
        # insert openid表
        sql_ins3 = """insert into {tableo}({tableo_uid}, {tableo_aid}, {tableo_oid})
                    values(%(uid)s,%(aid)s,%(oid)s)
        """
        con.execute_sql(sql_ins3.format(**SQL_DIC_USEROPENID), {"uid": uid, "aid": app_id, "oid": openid})

    ret.msg = '注册成功'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())

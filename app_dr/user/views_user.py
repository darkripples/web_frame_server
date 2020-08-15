#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/11/30
@Author     :   fls    
@Contact    :   fls@darkripples.com
@Desc       :   darkripples总平台相关-用户相关

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/11/30 14:14   fls        1.0         create
2019/12/06 14:05   fls        1.1         增加保存或更换phone、email的接口
2020/08/14 16:05   fls        1.2         配合后台管理新增接口-登出、用户列表等
"""

from random import randint
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt

from app_dr.dr_utils import req_invalid_check

from ez_utils import connection, PwdCtrl, RedisCtrl, flog, sms_send, email_send, fmt_date, hump2underline
from ez_utils.models import ResModel, ResModelToLogin, ResPageModel

from conf import (REDIS_KEY_PRE_PWDERR, REDIS_KEY_PRE_SID, REDIS_KEY_PRE_SIDERR, REDIS_KEY_PRE_SMSCODE,
                  ALI_SMS_TMPL_RESET_PWD, REDIS_KEY_PRE_EMAILCODE, EMAIL_MODPWD_TITLE, EMAIL_MODPWD_CONT,
                  REDIS_KEY_PRE_CODEERR, ALI_SMS_TMPL_RESET_PHONE, EMAIL_MODPHONE_TITLE, EMAIL_MODPHONE_CONT,
                  REDIS_KEY_PRE_TOKEN, PAGE_DEFAULT_LIMIT)
from .models import SQL_DIC_USERINFO, DrUserInfo, SQL_DIC_USER, DrUser, SQL_DIC_ROLES, SQL_DIC_USERROLE


@require_POST
@csrf_exempt
def log_out(req):
    """
    登出
    :param req:
    :return:
    """
    ret = ResModel()

    token = req.META.get('HTTP_TOKEN')
    if token:
        # 获取redis缓存数据
        r = RedisCtrl()
        r.del_one(REDIS_KEY_PRE_TOKEN + token)
    ret.code = ret.ResCode.succ
    ret.msg = "已退出登录"
    return JsonResponse(ret.to_dic())


@require_GET
def get_list(req):
    """
    用户列表
    :param req:
    :return:
    """
    ret = ResPageModel()

    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        return JsonResponse(ret.to_dic())

    ret.page = req.GET.get('page', '1')
    ret.limit = req.GET.get('limit', PAGE_DEFAULT_LIMIT)
    order_field = hump2underline(req.GET.get('orderField', ''))
    order_type = req.GET.get('orderType', '')

    role_id = req.GET.get('roleId', '')
    uid = req.GET.get('id', '')
    acc = req.GET.get('account', '')
    name = req.GET.get('name', '')

    # 查询条件
    par_dic = {}
    sub_sql_role = ""
    if role_id:
        sub_sql_role = ' and r.{tabler_id}=%(role_id)s'
        par_dic['role_id'] = role_id

    # 数据查询sql
    sql = """select 
                u.{table1_id} as id,u.{table1_account} as account,u.{table1_uname} as user_name,u.{table1_phone} as phone,
                u.{table1_email} as email,u.{table1_emailsucc} as emailsucc,
                ui.{table11_sex} as sex_type,ui.{table11_himg} as head_img, ui.{table11_introduce} as user_introduce,
                ui.{table11_occupation} as occupation,
                aa.role_ids, aa.role_names,
                to_char(u.{table1_atime}, 'yyyy-mm-dd hh24:mi:ss') as add_time
            from {table1} as u
            inner join {table11} ui on ui.{table11_id}=u.{table1_id}
            inner join (
                select urn.user_id, string_agg(urn.role_name, ',') role_names, string_agg(urn.role_id, ',') role_ids 
                from 
                (select ur.{table3_uid} as user_id,r.{tabler_id} as role_id,r.{tabler_name} as role_name 
                    from {tabler} r,{table3} ur
                    where ur.{table3_rid}=r.{tabler_id}
                    %s
                ) urn 
            group by urn.user_id
            ) aa on aa.user_id=u.{table1_id}
            where 1=1
        """ % sub_sql_role
    sql_count = """select count(1) as cnt
            from {table1} as u
            inner join {table11} ui on ui.{table11_id}=u.{table1_id}
            inner join (
                select urn.user_id, string_agg(urn.role_name, ',') role_names, string_agg(urn.role_id, ',') role_ids 
                from 
                (select ur.{table3_uid} as user_id,r.{tabler_id} as role_id,r.{tabler_name} as role_name 
                    from {tabler} r,{table3} ur
                    where ur.{table3_rid}=r.{tabler_id}
                    %s
                ) urn 
            group by urn.user_id
            ) aa on aa.user_id=u.{table1_id}
            where 1=1
        """ % sub_sql_role

    # 查询条件
    if uid:
        sql += " and u.{table1_id}=%(uid)s"
        sql_count += " and u.{table1_id}=%(uid)s"
        par_dic['uid'] = uid
    if acc:
        sql += " and u.{table1_account} like %(acc)s"
        sql_count += " and u.{table1_account} like %(acc)s"
        par_dic['acc'] = f"%{acc}%"
    if name:
        sql += " and u.{table1_uname} like %(name)s"
        sql_count += " and u.{table1_uname} like %(name)s"
        par_dic['name'] = f"%{name}%"

    # 排序
    if order_field:
        sql += f" order by {order_field} {order_type}"
    else:
        sql += " order by u.{table1_uname} asc "

    with connection() as con:
        rs = con.execute_sql(
            sql_count.format(**{**SQL_DIC_USER, **SQL_DIC_USERINFO, **SQL_DIC_ROLES, **SQL_DIC_USERROLE}),
            par_dic)
        ret.rsCount = rs[0].cnt
        # dicorobj需为dict
        ret.data = con.execute_sql(
            sql.format(**{**SQL_DIC_USER, **SQL_DIC_USERINFO, **SQL_DIC_ROLES, **SQL_DIC_USERROLE}),
            par_dic, dicorobj="dict", page=ret.page,
            limit=ret.limit)

    ret.code = ret.ResCode.succ
    ret.msg = ""
    return JsonResponse(ret.to_dic())


@require_GET
def get_info(req):
    """
    查询信息
    :param req:
    :return:
    """
    ret = ResModel()
    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        return JsonResponse(ret.to_dic())
    # 中间件校验token后赋值USER_ID
    user_id = req.META.get("USER_ID")
    if user_id:
        # 查询用户信息
        with connection() as con:
            user_rs = con.execute_sql("""
                select a.{table1_uname},a.{table1_phone},a.{table1_email},a.{table1_emailsucc},
                    a.{table1_wx},a.{table1_qq},to_char(a.{table1_atime}, 'yyyy-mm-dd hh24:mi:ss') as {table1_atime},
                    b.{table11_sex},b.{table11_himg},b.{table11_introduce},b.{table11_notes},b.{table11_occupation},
                    b.{table11_local}
                from {table1} a,{table11} b 
                where a.{table1_id}=b.{table11_id} and a.{table1_id}=%(uid)s""".format(
                **{**SQL_DIC_USER, **SQL_DIC_USERINFO}), {"uid": user_id}, dicorobj='dict')
            if user_rs and user_rs[0]:
                ret.data = user_rs[0]
    ret.code = ret.ResCode.succ
    ret.msg = ""
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def modify_info(req):
    """
    修改信息
    :param req:
    :return:
    """
    ret = ResModel()
    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        return JsonResponse(ret.to_dic())
    # 中间件校验token后赋值USER_ID
    user_id = req.META.get("USER_ID")
    if not user_id:
        return JsonResponse(ResModelToLogin().to_dic())

    # 校验用户信息
    with connection() as con:
        user_rs = con.execute_sql("""select {table11_id} 
            from {table11} where {table11_id}=%(uid)s""".format(**SQL_DIC_USERINFO), {"uid": user_id})
        if (not user_rs) or (not user_rs[0]):
            # 按理说不会走这个if的，若走了，肯定有问题，不必友好提示
            return JsonResponse(ResModelToLogin().to_dic())

    # 获取参数,不取默认值是为了保持数据库的default值
    sex_type = req.POST.get('sexType', DrUserInfo.SEX_TYPE[0][0])
    head_img = req.POST.get('headImg', '')
    user_introduce = req.POST.get('userIntro', '')
    user_notes = req.POST.get('userNotes', '')
    occupation = req.POST.get('userOcc', '')
    user_location = req.POST.get('userLocal', '')
    with connection() as con:
        con.execute_sql("""update {table11} 
            set {table11_sex}=%(sex)s,{table11_himg}=%(himg)s,{table11_introduce}=%(intro)s,
                {table11_notes}=%(notes)s,{table11_occupation}=%(occ)s,{table11_local}=%(local)s 
            where {table11_id}=%(uid)s""".format(**SQL_DIC_USERINFO),
                        {"uid": user_id, "sex": sex_type, "himg": head_img, "intro": user_introduce,
                         "notes": user_notes, "occ": occupation, "local": user_location})

    ret.msg = '已修改'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def modify_pwd(req):
    """
    修改密码
    :param req:
    :return:
    """
    ret = ResModel()
    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        return JsonResponse(ret.to_dic())
    # 中间件校验token后赋值USER_ID
    user_id = req.META.get("USER_ID")
    if not user_id:
        return JsonResponse(ResModelToLogin().to_dic())

    old_pwd = req.POST.get('oldPwd', '').upper()
    new_pwd = req.POST.get('newPwd', '').upper()
    if (not old_pwd) or (not new_pwd):
        ret.msg = "请求参数缺失"
        return JsonResponse(ret.to_dic())

    # db前校验
    r = RedisCtrl()
    if r.get_one(REDIS_KEY_PRE_PWDERR + user_id + "_ERR"):
        ret.msg = "原密码错误,请" + str(r.get_ex_time(REDIS_KEY_PRE_PWDERR + user_id + "_ERR")) + "秒后再尝试"
        return JsonResponse(ret.to_dic())

    # 校验用户信息
    with connection() as con:
        user_rs = con.execute_sql("""select {table1_pwd},{table1_salt}
                from {table1} where {table1_id}=%(uid)s""".format(**SQL_DIC_USER), {"uid": user_id})
        if (not user_rs) or (not user_rs[0]):
            # 按理说不会走这个if的，若走了，肯定有问题，不必友好提示
            return JsonResponse(ResModelToLogin().to_dic())
        user_rs = user_rs[0]

    # 密码校验
    p = PwdCtrl()
    if user_rs.pwdValue.upper() != p.create_md5(src_str=old_pwd, salt=user_rs.pwdSalt):
        # 密码校验不通过
        ret.msg = '原密码错误'
        # 错误次数，5分钟内，不可大于等于10次
        err_cnt = r.get_one(REDIS_KEY_PRE_PWDERR + user_id)
        if not err_cnt:
            err_cnt = 1
            r.set_one(REDIS_KEY_PRE_PWDERR + user_id, str(err_cnt), expt=60 * 5)
        else:
            err_cnt = int(err_cnt) + 1
            r.set_one(REDIS_KEY_PRE_PWDERR + user_id, str(err_cnt), expt=60 * 5)
        if int(err_cnt) >= 10:
            r.del_one(REDIS_KEY_PRE_PWDERR + user_id)
            # 同一个手机号验证码尝试次数过多
            flog.warning(f"修改密码时ID[{user_id}]用户的原密码尝试次数过多")
            r.set_one(REDIS_KEY_PRE_PWDERR + user_id + "_ERR", "ERR", expt=60 * 5)
            ret.msg = '原密码错误，请重新加载'
        return JsonResponse(ret.to_dic())

    # 修改
    salt = p.get_salt()
    pwd = p.create_md5(new_pwd, salt=salt)
    with connection() as con:
        con.execute_sql("""update {table1} set {table1_pwd}=%(pwd)s,{table1_salt}=%(salt)s
                where {table1_id}=%(uid)s""".format(**SQL_DIC_USER), {"uid": user_id, "pwd": pwd, "salt": salt})

    ret.msg = '已修改'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def sms_reset_pwd(req, sid, vcode):
    """
    修改密码-发送短信验证码
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
    # 中间件校验token后赋值USER_ID
    user_id = req.META.get("USER_ID")
    if not user_id:
        ret.msg = "用户信息不存在"
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

    # 查询用户信息
    with connection() as con:
        user_rs = con.execute_sql(
            "select {table1_phone}, {table1_id} from {table1} where {table1_id}=%(uid)s".format(**SQL_DIC_USER),
            {"uid": user_id})
        if user_rs and user_rs[0]:
            user_obj = user_rs[0]
            if not user_obj.phone:
                ret.msg = "您未绑定手机号"
                return JsonResponse(ret.to_dic())
        else:
            ret.msg = "用户信息不存在"
            return JsonResponse(ret.to_dic())

    # 短信验证码发送
    sms_code = "%06d" % randint(0, 999999)
    r.set_one(REDIS_KEY_PRE_SMSCODE + user_obj.id, sms_code, expt=60 * 5)
    sms_ret = sms_send(user_obj.phone, {"code": sms_code}, ALI_SMS_TMPL_RESET_PWD, "重置密码验证码")
    flog.debug(f"重置密码验证码发送:{sms_ret}")

    ret.msg = '已发送'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def email_reset_pwd(req, sid, vcode):
    """
    修改密码-发送email验证码
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
    # 中间件校验token后赋值USER_ID
    user_id = req.META.get("USER_ID")
    if not user_id:
        ret.msg = "用户信息不存在"
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

    # 查询用户信息
    with connection() as con:
        user_rs = con.execute_sql(
            "select {table1_id}, {table1_email} from {table1} where {table1_id}=%(uid)s".format(**SQL_DIC_USER),
            {"uid": user_id})
        if user_rs and user_rs[0]:
            user_obj = user_rs[0]
            if not user_obj.email:
                ret.msg = "您未绑定email地址"
                return JsonResponse(ret.to_dic())
        else:
            ret.msg = "用户信息不存在"
            return JsonResponse(ret.to_dic())

    # email验证码发送
    email_code = "%06d" % randint(0, 999999)
    r.set_one(REDIS_KEY_PRE_EMAILCODE + user_obj.id, email_code, expt=60 * 6)
    email_send([user_obj.email], EMAIL_MODPWD_TITLE, EMAIL_MODPWD_CONT % email_code)

    ret.msg = '已发送'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def reset_pwd(req, code_way, sid):
    """
    重置密码
    :param req:
    :param code_way: smscode.短信验证码;emailcode.email验证码
    :param sid:
    :return:
    """
    ret = ResModel()
    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        return JsonResponse(ret.to_dic())
    # 中间件校验token后赋值USER_ID
    user_id = req.META.get("USER_ID")
    if not user_id:
        ret.msg = "用户信息不存在"
        return JsonResponse(ret.to_dic())

    # 图形验证码or短信验证码
    auth_code = req.POST.get('authCode', '').upper()
    new_pwd = req.POST.get('newPwd', '').upper()
    if not auth_code:
        ret.msg = '验证码不可空'
        return JsonResponse(ret.to_dic())
    if not new_pwd:
        ret.msg = '新密码不可空'
        return JsonResponse(ret.to_dic())

    # 获取redis缓存数据
    r = RedisCtrl()
    verify_code = r.get_one(REDIS_KEY_PRE_SID + sid)
    if not verify_code:
        ret.msg = '验证码已过期'
        return JsonResponse(ret.to_dic())

    if code_way == 'emailcode':
        # 登录方式.emailcode.email验证码
        user_code = r.get_one(REDIS_KEY_PRE_EMAILCODE + user_id)
    elif code_way == 'smscode':
        # 登录方式.smscode.短信验证码
        user_code = r.get_one(REDIS_KEY_PRE_SMSCODE + user_id)
    else:
        # 其他code_way,反馈失败
        return JsonResponse(ret.to_dic())

    # 校验验证码
    if not user_code:
        # 短信验证码不存在
        ret.msg = '验证码已过期'
        return JsonResponse(ret.to_dic())
    if user_code != auth_code:
        # 校验验证码
        ret.msg = '验证码错误'
        # 记录错误次数，多次失败则需重新请求sid
        err_cnt = r.get_one(REDIS_KEY_PRE_CODEERR + user_id)
        if not err_cnt:
            err_cnt = 1
            r.set_one(REDIS_KEY_PRE_CODEERR + user_id, str(err_cnt), expt=60 * 5)
        else:
            err_cnt = int(err_cnt) + 1
            r.set_one(REDIS_KEY_PRE_CODEERR + user_id, str(err_cnt), expt=60 * 5)
        if int(err_cnt) >= 10:
            # 尝试次数大于10次，则需重新发送sms
            r.del_one(REDIS_KEY_PRE_SMSCODE + user_id)
            r.del_one(REDIS_KEY_PRE_EMAILCODE + user_id)
            r.del_one(REDIS_KEY_PRE_CODEERR + user_id)
            # 同一个验证码尝试次数过多
            flog.warning(f"重置密码时[{user_id}]用户的验证码尝试次数过多")
            ret.msg = '验证码错误，请重新加载'
        return JsonResponse(ret.to_dic())

    # 设置密码
    p = PwdCtrl()
    salt = p.get_salt()
    pwd = p.create_md5(src_str=new_pwd, salt=salt)
    with connection() as con:
        con.execute_sql("""update {table1} set {table1_pwd}=%(pwd)s,{table1_salt}=%(salt)s ,{table1_utime}=%(ut)s
        where {table1_id}=%(uid)s""".format(**SQL_DIC_USER),
                        {"pwd": pwd, "uid": user_id, "salt": salt, "ut": fmt_date()})
    ret.msg = '已修改密码'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def sms_reset_phone(req, sid, vcode):
    """
    发送短信验证码-更换/添加手机号
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
    # 中间件校验token后赋值USER_ID
    user_id = req.META.get("USER_ID")
    if not user_id:
        ret.msg = "用户信息不存在"
        return JsonResponse(ret.to_dic())
    phone = req.POST.get("phone")
    if not phone:
        ret.msg = "请输入新手机号"
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

    # 查询用户信息
    with connection() as con:
        user_rs = con.execute_sql(
            "select {table1_id} from {table1} where {table1_id}=%(uid)s".format(**SQL_DIC_USER),
            {"uid": user_id})
        if not user_rs:
            ret.msg = "用户信息不存在"
            return JsonResponse(ret.to_dic())
        # 新手机号重复性校验
        user_rs2 = con.execute_sql(
            "select {table1_id} from {table1} where {table1_phone}=%(phone)s".format(**SQL_DIC_USER),
            {"phone": phone})
        if user_rs2:
            ret.msg = "该手机号已被使用"
            return JsonResponse(ret.to_dic())

    # 短信验证码发送
    sms_code = "%06d" % randint(0, 999999)
    r.set_one(REDIS_KEY_PRE_SMSCODE + phone, sms_code, expt=60 * 5)
    sms_ret = sms_send(phone, {"code": sms_code}, ALI_SMS_TMPL_RESET_PHONE, "修改手机号验证码")
    flog.debug(f"修改手机号验证码发送:{sms_ret}")

    ret.msg = '已发送'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def email_reset_email(req, sid, vcode):
    """
    发送email验证码-更换/添加email
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
    # 中间件校验token后赋值USER_ID
    user_id = req.META.get("USER_ID")
    if not user_id:
        ret.msg = "用户信息不存在"
        return JsonResponse(ret.to_dic())
    email = req.POST.get("email")
    if not email:
        ret.msg = "请输入新EMAIL"
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

    # 查询用户信息
    with connection() as con:
        user_rs = con.execute_sql(
            "select {table1_id} from {table1} where {table1_id}=%(uid)s".format(**SQL_DIC_USER),
            {"uid": user_id})
        if not user_rs:
            ret.msg = "用户信息不存在"
            return JsonResponse(ret.to_dic())
        # 新email重复性校验
        user_rs2 = con.execute_sql(
            "select {table1_id} from {table1} where {table1_email}=%(email)s".format(**SQL_DIC_USER),
            {"email": email})
        if user_rs2:
            ret.msg = "该email已被使用"
            return JsonResponse(ret.to_dic())

    # email验证码发送
    email_code = "%06d" % randint(0, 999999)
    r.set_one(REDIS_KEY_PRE_EMAILCODE + email, email_code, expt=60 * 6)
    send_ret = email_send([email], EMAIL_MODPHONE_TITLE, EMAIL_MODPHONE_CONT % email_code)
    flog.debug(email + f"重置密码时发送email验证码err:{send_ret}")

    ret.msg = '已发送'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def reset_phone_email(req, code_way, sid):
    """
    更换/添加手机号、email
    :param req:
    :param code_way: smscode.短信验证码;emailcode.email验证码
    :param sid:
    :return:
    """
    ret = ResModel()
    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        return JsonResponse(ret.to_dic())
    # 中间件校验token后赋值USER_ID
    user_id = req.META.get("USER_ID")
    if not user_id:
        ret.msg = "用户信息不存在"
        return JsonResponse(ret.to_dic())

    # 图形验证码or短信验证码
    auth_code = req.POST.get('authCode', '').upper()
    # 新phone或者新email
    new_aim = req.POST.get('newAim', '')
    if not auth_code:
        ret.msg = '验证码不可空'
        return JsonResponse(ret.to_dic())
    if not new_aim:
        ret.msg = '参数异常'
        return JsonResponse(ret.to_dic())

    # 获取redis缓存数据
    r = RedisCtrl()
    verify_code = r.get_one(REDIS_KEY_PRE_SID + sid)
    if not verify_code:
        ret.msg = '验证码已过期'
        return JsonResponse(ret.to_dic())

    if code_way == 'emailcode':
        # 登录方式.emailcode.email验证码
        user_code = r.get_one(REDIS_KEY_PRE_EMAILCODE + new_aim)
        ret.msg = '该email验证码已过期'
        sub_sql = "{table1_email}=%(new)s,{table1_emailsucc}='" + DrUser.EMAIL_SUCC[1][0] + "',"
    elif code_way == 'smscode':
        # 登录方式.smscode.短信验证码
        user_code = r.get_one(REDIS_KEY_PRE_SMSCODE + new_aim)
        ret.msg = '该手机号验证码已过期'
        sub_sql = "{table1_phone}=%(new)s,"
    else:
        # 其他code_way,反馈失败
        return JsonResponse(ret.to_dic())

    # 校验验证码
    if not user_code:
        # 验证码不存在
        return JsonResponse(ret.to_dic())
    if user_code != auth_code:
        # 校验验证码
        ret.msg = '验证码错误'
        # 记录错误次数，多次失败则需重新请求sid
        err_cnt = r.get_one(REDIS_KEY_PRE_CODEERR + user_id)
        if not err_cnt:
            err_cnt = 1
            r.set_one(REDIS_KEY_PRE_CODEERR + user_id, str(err_cnt), expt=60 * 5)
        else:
            err_cnt = int(err_cnt) + 1
            r.set_one(REDIS_KEY_PRE_CODEERR + user_id, str(err_cnt), expt=60 * 5)
        if int(err_cnt) >= 10:
            # 尝试次数大于10次，则需重新发送sms
            r.del_one(REDIS_KEY_PRE_SMSCODE + user_id)
            r.del_one(REDIS_KEY_PRE_EMAILCODE + user_id)
            r.del_one(REDIS_KEY_PRE_CODEERR + user_id)
            # 同一个验证码尝试次数过多
            flog.warning(f"[{user_id}]用户的{code_way}验证码尝试次数过多")
            ret.msg = '验证码错误，请重新加载'
        return JsonResponse(ret.to_dic())

    # 设置
    with connection() as con:
        con.execute_sql("update {table1} set " + sub_sql + ",{table1_utime}=%(ut)s where {table1_id}=%(uid)s".format(
            **SQL_DIC_USER), {"new": new_aim, "uid": user_id, "ut": fmt_date()})

    ret.msg = '已修改'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())

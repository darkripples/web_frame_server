#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2020/08/14
@Author     :   fls    
@Contact    :   fls@darkripples.com
@Desc       :   角色管理

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/08/14 9:37   fls        1.0         create
"""
from json import loads
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from app_dr.dr_utils import req_invalid_check
from ez_utils import connection, RedisCtrl, hump2underline
from ez_utils.models import ResModel, ResPageModel
from conf import REDIS_KEY_PRE_TOKEN, PAGE_DEFAULT_LIMIT
from .models import SQL_DIC_ROLES, DrRoles


@require_GET
def get_list(req):
    """
    角色列表
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

    name = req.GET.get('name', '')
    rid = req.GET.get('id', '')

    # 查询用户角色，若为超管，则不限制visible条件
    filter_visible = True
    token = req.META.get('HTTP_TOKEN')
    r = RedisCtrl()
    user_info = r.get_one(REDIS_KEY_PRE_TOKEN + token)
    if user_info:
        user_info = loads(user_info)
        if DrRoles.type_sa in user_info['roles'].split(","):
            # 超管，不需限制visible条件
            filter_visible = False

    # 数据查询sql
    sql = """select {tabler_id}, {tabler_name}, {tabler_level}, {tabler_orderno},
        {tabler_note}, {tabler_visible},
        to_char({tabler_atime}, 'yyyy-mm-dd hh24:mi:ss') as {tabler_atime}
        from {tabler} a
        where 1=1
    """
    sql_count = """select count(1) as cnt
        from {tabler} a
        where 1=1
    """

    # 查询条件
    par_dic = {}
    if filter_visible:
        sql += " and a.{tabler_visible}=%(visible)s"
        sql_count += " and a.{tabler_visible}=%(visible)s"
        par_dic['visible'] = '1'
    if name:
        sql += " and {tabler_name} like %(name)s"
        sql_count += " and {tabler_name} like %(name)s"
        par_dic['name'] = f"%{name}%"
    if rid:
        sql += " and {tabler_id} = %(rid)s"
        sql_count += " and {tabler_id} = %(rid)s"
        par_dic['rid'] = rid

    # 排序
    if order_field:
        sql += f" order by {order_field} {order_type}"
    else:
        sql += " order by a.{tabler_orderno} asc "

    with connection() as con:
        rs = con.execute_sql(sql_count.format(**SQL_DIC_ROLES), par_dic)
        ret.rsCount = rs[0].cnt
        # dicorobj需为dict
        ret.data = con.execute_sql(sql.format(**SQL_DIC_ROLES), par_dic, dicorobj="dict", page=ret.page,
                                   limit=ret.limit)

    ret.code = ret.ResCode.succ
    ret.msg = ""
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def save_obj(req):
    """
    保存role
    :param req:
    :return:
    """
    ret = ResModel()

    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        return JsonResponse(ret.to_dic())

    mod_user_id = req.META.get('USER_ID')
    mod_type = req.POST.get('modType', '')
    rid = req.POST.get('id', '')
    rname = req.POST.get('name', '')
    rnote = req.POST.get('note', '')
    order_no = req.POST.get('orderNo', '0')

    if mod_type == 'upd':
        # 修改
        rs = DrRoles.objects.filter(id=rid)
        if not rs:
            ret.code = ret.ResCode.fail
            ret.msg = "未查询到该记录"
            return JsonResponse(ret.to_dic())
        rs.update(role_name=rname, note=rnote, order_no=order_no, upd_user_id=mod_user_id)
    else:
        # 新增
        rs = DrRoles.objects.filter(id=rid)
        if rs:
            # 该id已存在
            ret.code = ret.ResCode.fail
            ret.msg = "ID重复"
            return JsonResponse(ret.to_dic())
        # insert
        DrRoles.objects.create(id=rid, role_name=rname, note=rnote, order_no=order_no,
                               upd_user_id=mod_user_id, add_time=timezone.now())

    ret.code = ret.ResCode.succ
    ret.msg = "已保存"
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def del_obj(req):
    """
    删除role记录
    :param req:
    :return:
    """
    ret = ResModel()

    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        return JsonResponse(ret.to_dic())

    mod_user_id = req.META.get('USER_ID')
    rid = req.POST.get('id')
    if not rid:
        ret.code = ret.ResCode.fail
        ret.msg = "未查询记录"
        return JsonResponse(ret.to_dic())

    DrRoles.objects.filter(id=rid).delete()

    ret.code = ret.ResCode.succ
    ret.msg = "已删除"
    return JsonResponse(ret.to_dic())

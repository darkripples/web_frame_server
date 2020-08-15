#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2020/8/14
@Author     :   fls    
@Contact    :   fls@darkripples.com
@Desc       :   menu管理

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/14 15:55   fls        1.0         create
"""

from uuid import uuid1
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from app_dr.dr_utils import req_invalid_check
from ez_utils import connection, hump2underline
from ez_utils.models import ResModel, ResPageModel
from conf import PAGE_DEFAULT_LIMIT
from .models import SQL_DIC_MENU, DrMenu


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
    rid = req.GET.get('rid', '')
    no_id = req.GET.get('noId', '')
    pid = req.GET.get('pId', '')

    # 数据查询sql
    sql = """select a.{tablem_id}, a.{tablem_pid}, a.{tablem_sname}, a.{tablem_aname},
        a.{tablem_href}, a.{tablem_icon}, a.{tablem_orderno}, 
        to_char(a.{tablem_atime}, 'yyyy-mm-dd hh24:mi:ss') as {tablem_atime},
        b.{tablem_sname} as parent_name
        from {tablem} a
        left join {tablem} b on a.{tablem_pid}=b.{tablem_id}
        where 1=1
    """
    sql_count = """select count(1) as cnt
        from {tablem} a
        left join {tablem} b on a.{tablem_pid}=b.{tablem_id}
        where 1=1
    """

    # 查询条件
    par_dic = {}
    if name:
        sql += " and (a.{tablem_sname} like %(name)s or a.{tablem_aname} like %(name)s)"
        sql_count += " and (a.{tablem_sname} like %(name)s or a.{tablem_aname} like %(name)s)"
        par_dic['name'] = f"%{name}%"
    if rid:
        sql += " and a.{tablem_id} = %(mid)s"
        sql_count += " and a.{tablem_id} = %(mid)s"
        par_dic['mid'] = rid
    if pid:
        sql += " and( a.{tablem_id} = %(pid)s or a.{tablem_pid} = %(pid)s)"
        sql_count += " and( a.{tablem_id} = %(pid)s or a.{tablem_pid} = %(pid)s)"
        par_dic['pid'] = pid
    if no_id:
        sql += " and a.{tablem_id} != %(nid)s"
        sql_count += " and a.{tablem_id} != %(nid)s"
        par_dic['nid'] = no_id

    # 排序
    if order_field:
        sql += f" order by {order_field} {order_type}"
    else:
        sql += " order by a.{tabler_orderno} asc "

    with connection() as con:
        rs = con.execute_sql(sql_count.format(**SQL_DIC_MENU), par_dic)
        ret.rsCount = rs[0].cnt
        # dicorobj需为dict
        ret.data = con.execute_sql(sql.format(**SQL_DIC_MENU), par_dic, dicorobj="dict", page=ret.page,
                                   limit=ret.limit)

    ret.code = ret.ResCode.succ
    ret.msg = ""
    return JsonResponse(ret.to_dic())


@require_GET
def get_display_list(req):
    """
    角色列表-带pid的树形
    :param req:
    :return:
    """
    ret = ResModel()

    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        return JsonResponse(ret.to_dic())

    with connection() as con:
        ret.data = con.execute_sql("""select a.{tablem_id} as id,a.{tablem_aname} as name,a.{tablem_pid} as p_id 
        from {tablem} a where 1=1 order by a.{tablem_orderno} asc,a.{tablem_id} asc""".format(**SQL_DIC_MENU),
                                   dicorobj="dict")
    ret.code = ret.ResCode.succ
    ret.msg = ""
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def del_obj(req):
    """
    删除
    :param req:
    :return:
    """
    ret = ResModel()

    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        return JsonResponse(ret.to_dic())

    mid = req.POST.get('id')
    if not mid:
        ret.code = ret.ResCode.fail
        ret.msg = "未查询到记录"
        return JsonResponse(ret.to_dic())

    rs = DrMenu.objects.filter(id=mid)
    if not rs:
        ret.code = ret.ResCode.fail
        ret.msg = "未查询到记录"
        return JsonResponse(ret.to_dic())
    rs.delete()

    ret.code = ret.ResCode.succ
    ret.msg = "已删除"
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def save_obj(req, mod_type):
    """
    保存
    :param req:
    :param mod_type:
    :return:
    """
    ret = ResModel()

    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        return JsonResponse(ret.to_dic())

    mod_user_id = req.META.get('USER_ID')
    mid = req.POST.get("id")
    aname = req.POST.get("aliasName")
    icon = req.POST.get("icon")
    sname = req.POST.get("showName")
    pid = req.POST.get("parentId")
    href = req.POST.get("href")
    order_no = req.POST.get("orderNo")

    if pid and (not DrMenu.objects.filter(id=pid)):
        ret.code = ret.ResCode.fail
        ret.msg = "未查询到父节点"
        return JsonResponse(ret.to_dic())

    if mod_type == 'upd':
        # 修改
        rs = DrMenu.objects.filter(id=mid)
        if not rs:
            ret.code = ret.ResCode.fail
            ret.msg = "未查询到该记录"
            return JsonResponse(ret.to_dic())
        rs.update(pid=pid, show_name=sname, alias_name=aname, href=href, icon=icon,
                  order_no=order_no, upd_user_id=mod_user_id)
    else:
        # 新增
        DrMenu.objects.create(id=str(uuid1()).replace('-', ''), pid=pid, show_name=sname, alias_name=aname, href=href,
                              icon=icon, order_no=order_no, upd_user_id=mod_user_id, add_time=timezone.now())
    ret.code = ret.ResCode.succ
    ret.msg = "已保存"
    return JsonResponse(ret.to_dic())

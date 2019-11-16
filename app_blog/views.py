# coding:utf8

"""
# @Time : 2019/8/30 14:53
# @Author : fls
# @Desc: blog相关
"""
import traceback

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from ez_utils.models import ResPageModel, ResModel
from ez_utils import connection, get_ip
from ez_utils import fls_log

flog = fls_log(handler_name="app_blog.views")

from .models import SQL_DIC_TYPE, SQL_DIC_BLOG, SQL_DIC_PARAM
from . import app_name

from app_dr.dr_utils import add_visitor, req_invalid_check

from conf import PAGE_DEFAULT_LIMIT, SET_TITLE_CMD


@require_GET
def indexList(req):
    """
    2019/08/30 fls
    查询blog列表
    :param req: request
    :return:
    """
    ret = ResPageModel()

    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        ret.data = []
        return JsonResponse(ret.to_dic())

    blog_type = req.GET.get('type', '')

    ret.page = req.GET.get('page', '1')
    ret.limit = req.GET.get('limit', PAGE_DEFAULT_LIMIT)

    # todo 权限level的控制
    # 采用源生sql，方便where条件和分页,后期计划加入用户表的关联查询
    sql = "select a.{table1_id},a.{table1_title},b.{table2_type_name},a.{table1_tags},a.{table1_notes},a.{table1_aname}," \
          "to_char(a.{table1_atime}, 'yyyy-mm-dd hh24:mi:ss') as {table1_atime}, a.{table1_rlevel},a.{table1_rcnt}  " \
          "from {table1} a, {table2} b where a.{table1_type_id}=b.{table2_type_id} and a.{table1_rcnt}>=0".format(
        **SQL_DIC_BLOG)
    sql_count = "select count(1) as cnt " \
                "from {table1} a, {table2} b where a.{table1_type_id}=b.{table2_type_id} and {table1_rcnt}>=0".format(
        **SQL_DIC_BLOG)

    # 查询条件
    par_dic = {}
    if blog_type:
        # 类型
        sql += " and a.{table1_type_id}=%(blog_type)s".format(**SQL_DIC_BLOG)
        sql_count += " and a.{table1_type_id}=%(blog_type)s".format(**SQL_DIC_BLOG)
        par_dic['blog_type'] = blog_type

    # 排序
    sql += " order by a.{table1_atime} desc ".format(**SQL_DIC_BLOG)

    with connection() as con:
        rs = con.execute_sql(sql_count, par_dic)
        ret.rsCount = rs[0].cnt
        # dicorobj需为dict
        ret.data = con.execute_sql(sql, par_dic, dicorobj="dict", page=ret.page, limit=ret.limit)

    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@require_GET
def contentDetail(req, id):
    """
    查询blog明细
    :param req: request
    :param id: id
    :return:
    """

    ret = ResModel()
    ret.msg = req_invalid_check(req)

    # 浏览者信息
    v_cnt = 0
    try:
        ip = get_ip(req)
        v_cnt = add_visitor(ip, app_name, 'read', id)
    except:
        flog.log_error("记录访客信息失败:%s", traceback.format_exc())

    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        ret.data = {}
        return JsonResponse(ret.to_dic())

    ret.code = ret.ResCode.succ

    # todo 权限level的控制
    # 为了统一，驼峰命名，采用原生sql
    with connection() as con:
        rs = con.execute_sql(
            "select {table1_id},{table1_title},{table1_content},{table1_rcnt}," \
            "to_char({table1_atime}, 'yyyy-mm-dd hh24:mi:ss') as {table1_atime},{table1_notes},{table1_bgurl},{table1_rlevel} " \
            "from {table1} where {table1_id}=%(id)s and {table1_rcnt}>=0".format(**SQL_DIC_BLOG),
            {"id": id}, dicorobj="dict")
        if rs:
            ret.data = rs[0]
            if v_cnt == 1:
                con.execute_sql(
                    "update {table1} set {table1_rcnt}={table1_rcnt}+1 where {table1_id}=%(id)s".format(**SQL_DIC_BLOG),
                    {"id": id})
        else:
            ret.data = {}
    return JsonResponse(ret.to_dic())


@require_GET
def typeList(req):
    """
    查询blog类别
    :param req: request
    :return:
    """
    ret = ResModel()
    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        ret.data = []
        return JsonResponse(ret.to_dic())

    ret.code = ret.ResCode.succ
    with connection() as con:
        ret.data = con.execute_sql(
            "select {table2_type_id}, {table2_type_name} "
            "from {table2} order by convert_to({table2_type_name} , 'GB18030') asc".format(**SQL_DIC_TYPE),
            dicorobj="dict")
    return JsonResponse(ret.to_dic())


@require_GET
def titleValue(req):
    """
    查询副标题参数
    :param req: request
    :return:
    """
    ret = ResModel()
    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        ret.data = {}
        return JsonResponse(ret.to_dic())

    ret.code = ret.ResCode.succ
    with connection() as con:
        rs = con.execute_sql("select {table1_value} from {table1} where {table1_code}=%(p)s ".format(**SQL_DIC_PARAM),
                             {'p': SET_TITLE_CMD},
                             dicorobj="dict")
        ret.data = rs[0] if rs else {}
    return JsonResponse(ret.to_dic())

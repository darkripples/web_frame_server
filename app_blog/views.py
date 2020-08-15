#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/08/30
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   blog相关

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/08/30 14:53   fls        1.0         create
2020/08/14 17:53   fls        1.1         新增接口-新增blog
"""

from uuid import uuid1
from json import loads
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from django.utils import timezone

from ez_utils.models import ResPageModel, ResModel, ResModelToLogin
from ez_utils import connection, get_ip, flog, RedisCtrl

from .models import SQL_DIC_TYPE, SQL_DIC_BLOG, SQL_DIC_PARAM, BlogContent, BlogType

#from app_dr.wechat.utils import SET_TITLE_CMD
SET_TITLE_CMD = "fls" # todo 前缀，需自己配置
from app_dr.dr_utils import add_visitor, req_invalid_check

from conf import PAGE_DEFAULT_LIMIT, REDIS_KEY_PRE_TOKEN


@require_GET
def index_list(req):
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
    title = req.GET.get('title', '')
    rlevel = req.GET.get('rlevel', '0')

    ret.page = req.GET.get('page', '1')
    ret.limit = req.GET.get('limit', PAGE_DEFAULT_LIMIT)

    # todo 权限level的控制
    # 采用源生sql，方便where条件和分页,后期计划加入用户表的关联查询
    sql = """select a.{table1_id},a.{table1_title},b.{table2_type_name},a.{table1_tags},a.{table1_notes},
            a.{table1_aname}, to_char(a.{table1_atime}, 'yyyy-mm-dd hh24:mi:ss') as {table1_atime}, 
            a.{table1_rlevel},a.{table1_rcnt},a.{table1_type_id}
          from {table1} a, {table2} b where a.{table1_type_id}=b.{table2_type_id} and a.{table1_rlevel}>=%(rlevel)s""".format(
        **SQL_DIC_BLOG)
    sql_count = """select count(1) as cnt 
                from {table1} a, {table2} b where a.{table1_type_id}=b.{table2_type_id} and {table1_rlevel}>=%(rlevel)s""".format(
        **SQL_DIC_BLOG)

    # 查询条件
    par_dic = {"rlevel": rlevel}
    if blog_type:
        # 类型
        sql += " and a.{table1_type_id}=%(blog_type)s".format(**SQL_DIC_BLOG)
        sql_count += " and a.{table1_type_id}=%(blog_type)s".format(**SQL_DIC_BLOG)
        par_dic['blog_type'] = blog_type
    if title:
        sql += " and (a.{table1_title} like %(title)s or a.{table1_notes} like %(title)s)"
        sql_count += " and (a.{table1_title} like %(title)s or a.{table1_notes} like %(title)s)"
        par_dic['title'] = f"%{title}%"

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
def content_detail(req, id):
    """
    查询blog明细
    :param req: request
    :param id: id
    :return:
    """

    ret = ResModel()
    ret.msg = req_invalid_check(req)

    v_cnt = 0
    if not req.GET.get("forManage"):
        # 不 通过管理端查询
        # 浏览者信息登记
        try:
            ip = get_ip(req)
            v_cnt = add_visitor(ip, apps.get_app_config('app_blog').name, 'read', id)
        except:
            from traceback import format_exc
            flog.error("记录访客信息失败:%s" % format_exc())

    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        ret.data = {}
        return JsonResponse(ret.to_dic())

    ret.code = ret.ResCode.succ

    # todo 权限level的控制
    # 为了统一，驼峰命名，采用原生sql
    with connection() as con:
        # where 条件 and {table1_rlevel}>=0  暂时先屏蔽
        rs = con.execute_sql(
            """select {table1_id},{table1_title},{table1_content},{table1_rcnt},
                to_char({table1_atime}, 'yyyy-mm-dd hh24:mi:ss') as {table1_atime},
                {table1_notes},{table1_bgurl},{table1_rlevel},{table1_type_id},{table1_tags}
            from {table1} where {table1_id}=%(id)s """.format(**SQL_DIC_BLOG),
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
def type_list(req):
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
            """select {table2_type_id}, {table2_type_name} 
            from {table2} order by convert_to({table2_type_name} , 'GB18030') asc""".format(**SQL_DIC_TYPE),
            dicorobj="dict")
    return JsonResponse(ret.to_dic())


@require_GET
def title_value(req):
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


@require_POST
@csrf_exempt
def save_blog(req, mod_type):
    """
    保存
    :param req:
    :param mod_type: add/upd
    :return:
    """
    ret = ResModel()

    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        return JsonResponse(ret.to_dic())

    # 入参的非空校验
    post_data = req.POST
    post_dic = {'title': post_data.get('title', ""), 'title_notes': post_data.get('titleNotes', ""),
                'blog_type': post_data.get('blogType', ""), 'blog_tags': post_data.get('blogTags', ""),
                'content': post_data.get('content', ""),
                }
    if "" in post_dic.values():
        ret.msg = '缺失字段:' + list(post_dic.keys())[list(post_dic.values()).index("")]
        return JsonResponse(ret.to_dic())

    # 可空的入参
    post_dic['id'] = post_data.get('id', '')
    post_dic['read_level'] = int(post_data.get('rLevel', '-1'))
    img_url = post_data.get('bgUrl')
    if not img_url:
        post_dic['bg_url'] = ""
    else:
        if img_url.startswith("/static"):
            post_dic['bg_url'] = img_url
        else:
            post_dic['bg_url'] = '/%s' % img_url.replace("\\", "/")

    # 字段长度校验
    for k, v in post_dic.items():
        length_ = BlogContent._meta.get_field(k).max_length
        if length_ and length_ < len(v):
            ret.msg = '内容超长:' + BlogContent._meta.get_field(k).verbose_name
            return JsonResponse(ret.to_dic())

    if not BlogType.objects.filter(type_id=post_dic["blog_type"]):
        ret.code = ret.ResCode.fail
        ret.msg = "类型不合法"
        return JsonResponse(ret.to_dic())

    post_dic["upd_time"] = timezone.now()
    # 登录用户信息
    token = req.META.get('HTTP_TOKEN')
    r = RedisCtrl()
    user_info = r.get_one(REDIS_KEY_PRE_TOKEN + token)
    if user_info:
        user_info = loads(user_info)
    else:
        # 冗余校验
        ret = ResModelToLogin()
        return JsonResponse(ret.to_dic())

    if mod_type == 'upd':
        # 修改
        rs = BlogContent.objects.filter(id=post_dic['id'])
        if not rs:
            ret.code = ret.ResCode.fail
            ret.msg = "未查询到该记录"
            return JsonResponse(ret.to_dic())
        post_dic["upd_account"] = user_info["account"]
        post_dic["upd_name"] = user_info["username"]
        rs.update(**post_dic)
    else:
        # 新增
        # insert
        post_dic["id"] = str(uuid1()).replace('-', '')
        post_dic["add_time"] = post_dic["upd_time"]
        post_dic["auth_account"] = user_info["account"]
        post_dic["auth_name"] = user_info["username"]
        BlogContent.objects.create(**post_dic)

    ret.code = ret.ResCode.succ
    ret.msg = "已保存"
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def del_blog(req, blog_id):
    """
    删除blog
    :param req:
    :param blog_id:
    :return:
    """
    ret = ResModel()

    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        ret.code = ret.ResCode.fail
        return JsonResponse(ret.to_dic())

    rs = BlogContent.objects.filter(id=blog_id)
    if not rs:
        ret.code = ret.ResCode.fail
        ret.msg = "未查询到记录"
        return JsonResponse(ret.to_dic())

    rs.delete()

    ret.code = ret.ResCode.succ
    ret.msg = "已删除"
    return JsonResponse(ret.to_dic())

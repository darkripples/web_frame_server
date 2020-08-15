#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2020/8/13
@Author     :   fls    
@Contact    :   fls@darkripples.com
@Desc       :   菜单及权限

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/8/13 11:32   fls        1.0         create
"""

from uuid import uuid1
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from ez_utils.models import ResModel
from ez_utils import connection, fmt_date
from app_dr.dr_utils import req_invalid_check
from app_dr.models import SQL_DIC_MENU, SQL_DIC_USER, SQL_DIC_USERROLE, SQL_DIC_ROLEMENU, DrMenu, DrRoleMenu


@require_GET
def get_allmenu2list(req):
    """
    get_allmenu2list
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
    sql = """select *
        from
            (select
                 prt.{tablem_id}        {tablem_id},
                 prt.{tablem_sname},
                 prt.{tablem_aname},
                 prt.{tablem_href},
                 prt.{tablem_icon},
                 prt.{tablem_orderno}    {tablem_orderno},
                 chd.{tablem_id}         child_id,
                 chd.{tablem_sname}      child_show_name,
                 chd.{tablem_aname}      child_alias_name,
                 chd.{tablem_href}       child_href,
                 chd.{tablem_icon}       child_icon,
                 chd.{tablem_orderno}    child_order_no,
                 chd.{tablem_pid}        child_parent_id
             from {tablem} prt
                      left join {tablem} chd on chd.{tablem_pid} = prt.{tablem_id}
             where prt.{tablem_pid} is null
                or prt.{tablem_pid} = '') menu
        where
                menu.child_id in (
                select rm.{tablerm_mid}
                from
                    {table1} u,
                    {table3} ur,
                    {tablerm} rm
                where
                    u.{table1_id} = ur.{table3_uid}
                  and ur.{table3_rid} = rm.{tablerm_rid}
                  and u.{table1_id} = %(uid)s)
           or (menu.{tablem_id} in (
            select rm.{tablerm_mid}
            from
                {table1} u,
                {table3} ur,
                {tablerm} rm
            where
                u.{table1_id} = ur.{table3_uid}
              and ur.{table3_rid} = rm.{tablerm_rid}
              and u.{table1_id} = %(uid)s) and (menu.child_id is null or menu.child_id = ''))
        order by menu.{tablem_orderno}, menu.child_order_no
    """
    ret.data = []
    menuIdLst = []
    with connection() as con:
        menu_list = con.execute_sql(
            sql.format(**{**SQL_DIC_MENU, **SQL_DIC_ROLEMENU, **SQL_DIC_USER, **SQL_DIC_USERROLE}),
            {"uid": user_id})
        for row in menu_list:
            if row.id in menuIdLst:
                continue
            menuIdLst.append(row.id)
            menuObj = {"menuId": row.id, "showName": row.showName, "aliasName": row.aliasName, "href": row.href,
                       "icon": row.icon, "orderNo": row.orderNo}
            if row.childId:
                menuObj["hasChildren"] = True
                parentId = row.id
                children = []
                for child in menu_list:
                    if parentId == child.childParentId:
                        childObj = {"menuId": child.childId, "showName": child.childShowName,
                                    "aliasName": child.childAliasName,
                                    "href": child.childHref,
                                    "icon": child.childIcon, "orderNo": child.childOrderNo}
                        children.append(childObj)

                menuObj["children"] = children
            else:
                menuObj["hasChildren"] = False
            ret.data.append(menuObj)
    ret.msg = ''
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


def menu_children(children, ids):
    """
    生成标准treeNode的Json数据
    :param children:
    :param ids:
    :return:
    """
    nodes = []
    for row in children:
        nodes1 = {"name": row.show_name, "label": row.show_name, "id": row.id, "href": row.href,
                  "orderNo": row.order_no, "icon": row.icon, "aliasName": row.alias_name}
        if row.id in ids:
            nodes1["checked"] = True
        else:
            nodes1["checked"] = False
        # 根据父级菜单id查询菜单且按照order_no正序取出
        menus = DrMenu.objects.filter(pid=row.id).order_by('order_no')
        if menus:
            nodes1["children"] = menu_children(menus, ids)
        nodes.append(nodes1)
    return nodes


@require_GET
def get_menulist_role(req, role_id=None):
    """
    根据角色获取菜单
    :param req:
    :param role_id:
    :return:
    """
    ret = ResModel()

    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        return JsonResponse(ret.to_dic())

    if role_id:
        roleMenus = DrRoleMenu.objects.filter()
    else:
        roleMenus = DrRoleMenu.objects.filter(role_id=role_id)

    # ids存储当前角色已有的菜单id
    ids = []
    for row in roleMenus:
        ids.append(row.menu_id)

    tops = DrMenu.objects.filter(Q(pid='') | Q(pid__isnull=True)).order_by('order_no')

    ret.data = menu_children(tops, ids)
    ret.msg = ''
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def save_menulist_role(req, role_id):
    """
    保存角色下的菜单
    :param req:
    :param role_id:
    :return:
    """
    ret = ResModel()

    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        return JsonResponse(ret.to_dic())

    # 中间件校验token后赋值USER_ID
    mod_user_id = req.META.get("USER_ID")
    mids = req.POST.get('ids', '')

    # 先删除要保存或修改的角色菜单，然后再添加
    sql_ins = """insert into {tablerm}({tablerm_id},{tablerm_rid},{tablerm_mid},{tablerm_upduid}, {tablerm_atime})
        values(%(rmid)s, %(rid)s, %(mid)s, %(uid)s, %(atime)s)
    """
    now_date = fmt_date()
    # 开启事务
    with connection() as con:
        con.execute_sql("delete from {tablerm} where {tablerm_rid}=%(rid)s".format(**SQL_DIC_ROLEMENU),
                        {"rid": role_id})
        if mids:
            for mid in mids.split(","):
                con.execute_sql(sql_ins.format(**SQL_DIC_ROLEMENU), {"rmid": str(uuid1()).replace('-', ''),
                                                                     "rid": role_id, "mid": mid, "uid": mod_user_id,
                                                                     "atime": now_date})
    ret.msg = '已保存'
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())

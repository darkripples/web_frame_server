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

from django.db import models

__all__ = ['DrMenu', 'DrRoleMenu',
           'SQL_DIC_MENU', 'SQL_DIC_ROLEMENU',
           ]


class DrMenu(models.Model):
    """
    menu
    """

    id = models.CharField(verbose_name='id', max_length=40, primary_key=True, db_column='id')
    pid = models.CharField(verbose_name='父级id', max_length=40, blank=True, null=True)
    show_name = models.CharField(verbose_name='名称', max_length=20, blank=True)
    alias_name = models.CharField(verbose_name='别名', max_length=20, blank=True)
    href = models.CharField(verbose_name='menu连接地址', max_length=100, blank=True, null=True)
    icon = models.CharField(verbose_name='icon', max_length=50, blank=True, null=True)
    order_no = models.IntegerField(verbose_name="序号", default=0)
    upd_user_id = models.CharField(verbose_name='修改人id', max_length=40, blank=True, null=True)
    add_time = models.DateTimeField(verbose_name="添加时间", blank=True, null=True)

    class Meta:
        db_table = "dr_menu"


SQL_DIC_MENU = {
    "tablem": DrMenu._meta.db_table,
    "tablem_id": DrMenu.id.field_name,
    "tablem_pid": DrMenu.pid.field_name,
    "tablem_sname": DrMenu.show_name.field_name,
    "tablem_aname": DrMenu.alias_name.field_name,
    "tablem_href": DrMenu.href.field_name,
    "tablem_icon": DrMenu.icon.field_name,
    "tablem_orderno": DrMenu.order_no.field_name,
    "tablem_upduid": DrMenu.upd_user_id.field_name,
    "tablem_atime": DrMenu.add_time.field_name,
}


class DrRoleMenu(models.Model):
    """
    role-menu
    """

    id = models.CharField(verbose_name='id', max_length=40, primary_key=True, db_column='id')
    role_id = models.CharField(verbose_name='角色id', max_length=40)
    menu_id = models.CharField(verbose_name='菜单id', max_length=40)
    upd_user_id = models.CharField(verbose_name='修改人id', max_length=40, blank=True, null=True)
    add_time = models.DateTimeField(verbose_name="添加时间", blank=True, null=True)

    class Meta:
        db_table = "dr_role_menu"


SQL_DIC_ROLEMENU = {
    "tablerm": DrRoleMenu._meta.db_table,
    "tablerm_id": DrRoleMenu.id.field_name,
    "tablerm_rid": DrRoleMenu.role_id.field_name,
    "tablerm_mid": DrRoleMenu.menu_id.field_name,
    "tablerm_upduid": DrRoleMenu.upd_user_id.field_name,
    "tablerm_atime": DrRoleMenu.add_time.field_name,
}

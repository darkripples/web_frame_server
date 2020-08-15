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

from django.urls import path
from .views_menu_role import get_allmenu2list, get_menulist_role, save_menulist_role
from .views_menu import (get_list as menu_get_list, get_display_list as menu_get_display_list, del_obj as menu_del_obj,
                         save_obj as menu_save_obj)

app_name = 'app_dr_menu_role'

urlpatterns = [
    # 根据token获取菜单
    path(r'getAllMenu2List/', get_allmenu2list),
    # 根据角色查询菜单
    path(r'menuAllList/<str:role_id>', get_menulist_role),
    # 根据角色查询菜单
    path(r'menuAllList/', get_menulist_role),
    # 保存角色下的菜单
    path(r'saveRights/<str:role_id>', save_menulist_role),

    # 菜单列表
    path(r'menuList/', menu_get_list),
    # 菜单列表-带pid的树形
    path(r'menuDisplay/', menu_get_display_list),
    # 菜单-删除
    path(r'menuDel/', menu_del_obj),
    # 菜单-保存
    path(r'menuSave/<str:mod_type>', menu_save_obj),
]

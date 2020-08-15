#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/11/26
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   darkripples总平台相关-用户相关
        # python manage.py makemigrations
        # python manage.py migrate
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/11/26 08:52   fls        1.0         create
"""

from django.db import models

__all__ = ['DrUser', 'DrUserInfo', 'DrRoles', 'DrUserRole', 'DrUserOpenId',
           'SQL_DIC_USER', 'SQL_DIC_USERINFO', 'SQL_DIC_ROLES', 'SQL_DIC_USERROLE', 'SQL_DIC_USEROPENID']


class DrUser(models.Model):
    """
    用户信息
    """

    # email_succ枚举，第一位需为默认值
    EMAIL_SUCC = (
        ('0', '未验证'), ('1', '已验证')
    )

    id = models.CharField(verbose_name='id', max_length=40, primary_key=True, db_column='id')
    account = models.CharField(verbose_name='用户账户', max_length=20, blank=True)
    user_name = models.CharField(verbose_name='用户名', max_length=50, blank=True)
    pwd_value = models.CharField(verbose_name='密码', max_length=32, blank=True)
    pwd_salt = models.CharField(verbose_name='密码盐值', max_length=10, blank=True)
    phone = models.CharField(verbose_name='手机号', max_length=11, blank=True)
    email = models.CharField(verbose_name='email', max_length=50, blank=True)
    email_succ = models.CharField(verbose_name='email是否验证', choices=EMAIL_SUCC, max_length=1, blank=True, null=True)
    wx_link_id = models.CharField(verbose_name='微信用户id', max_length=50, blank=True, null=True)
    qq_link_id = models.CharField(verbose_name='qq号', max_length=20, blank=True, null=True)
    add_time = models.DateTimeField(verbose_name="添加时间", blank=True, null=True)
    upd_time = models.DateTimeField(verbose_name="更新时间", blank=True, null=True)

    class Meta:
        db_table = "dr_user"


SQL_DIC_USER = {
    "table1": DrUser._meta.db_table,
    "table1_id": DrUser.id.field_name,
    "table1_account": DrUser.account.field_name,
    "table1_uname": DrUser.user_name.field_name,
    "table1_pwd": DrUser.pwd_value.field_name,
    "table1_salt": DrUser.pwd_salt.field_name,
    "table1_phone": DrUser.phone.field_name,
    "table1_email": DrUser.email.field_name,
    "table1_emailsucc": DrUser.email_succ.field_name,
    "table1_wx": DrUser.wx_link_id.field_name,
    "table1_qq": DrUser.qq_link_id.field_name,
    "table1_atime": DrUser.add_time.field_name,
    "table1_utime": DrUser.upd_time.field_name,
}


class DrUserInfo(models.Model):
    """
    用户信息详情
    """

    # sex_type枚举，第一位需为默认值
    SEX_TYPE = (
        ('9', '未指定'), ('1', '男'), ('0', '女')
    )

    id = models.CharField(verbose_name='id', max_length=40, primary_key=True, db_column='id')
    sex_type = models.CharField(verbose_name='性别', choices=SEX_TYPE, max_length=1, default='9')
    head_img = models.CharField(verbose_name='头像', max_length=50, blank=True, null=True)
    user_introduce = models.CharField(verbose_name='简介', max_length=100, blank=True, null=True)
    user_notes = models.TextField(verbose_name="个人说明", blank=True, null=True)
    occupation = models.CharField(verbose_name='职业', max_length=50, blank=True, null=True)
    user_p = models.CharField(verbose_name='地区_省', max_length=100, blank=True, null=True)
    user_c = models.CharField(verbose_name='地区_市', max_length=100, blank=True, null=True)
    user_a = models.CharField(verbose_name='地区_区', max_length=100, blank=True, null=True)
    user_location = models.CharField(verbose_name='地区', max_length=100, blank=True, null=True)
    add_time = models.DateTimeField(verbose_name="添加时间", blank=True, null=True)
    upd_time = models.DateTimeField(verbose_name="更新时间", blank=True, null=True)

    class Meta:
        db_table = "dr_user_info"


SQL_DIC_USERINFO = {
    "table11": DrUserInfo._meta.db_table,
    "table11_id": DrUserInfo.id.field_name,
    "table11_sex": DrUserInfo.sex_type.field_name,
    "table11_himg": DrUserInfo.head_img.field_name,
    "table11_introduce": DrUserInfo.user_introduce.field_name,
    "table11_notes": DrUserInfo.user_notes.field_name,
    "table11_p": DrUserInfo.user_p.field_name,
    "table11_c": DrUserInfo.user_c.field_name,
    "table11_a": DrUserInfo.user_a.field_name,
    "table11_occupation": DrUserInfo.occupation.field_name,
    "table11_local": DrUserInfo.user_location.field_name,
    "table11_atime": DrUserInfo.add_time.field_name,
    "table11_utime": DrUserInfo.upd_time.field_name,
}


class DrRoles(models.Model):
    """
    角色信息
    """
    type_sa = "sa"
    type_user = "l1"

    ROLE_TYPE = (
        (type_sa, '超管'), (type_user, '普通用户'),
    )
    LEVEL_MAP = (
        ('1', '系统级'), ('2', '用户级')
    )

    id = models.CharField(verbose_name='id', max_length=10, primary_key=True, db_column='id')
    role_name = models.CharField(verbose_name='角色名', max_length=20, blank=True)
    level = models.CharField(verbose_name='级别：1-系统级；2-用户级', choices=LEVEL_MAP, max_length=1, blank=True, default='2')
    visible = models.CharField(verbose_name='此角色是否对普通用户可见', max_length=1, blank=True, default='1')
    note = models.CharField(verbose_name='备注', max_length=50, blank=True, null=True)
    order_no = models.IntegerField(verbose_name="序号", default=0)
    upd_user_id = models.CharField(verbose_name='修改人id', max_length=40, blank=True, null=True)
    add_time = models.DateTimeField(verbose_name="添加时间", blank=True, null=True)

    class Meta:
        db_table = "dr_roles"


SQL_DIC_ROLES = {
    "tabler": DrRoles._meta.db_table,
    "tabler_id": DrRoles.id.field_name,
    "tabler_name": DrRoles.role_name.field_name,
    "tabler_level": DrRoles.level.field_name,
    "tabler_visible": DrRoles.visible.field_name,
    "tabler_note": DrRoles.note.field_name,
    "tabler_orderno": DrRoles.order_no.field_name,
    "tabler_upduid": DrRoles.upd_user_id.field_name,
    "tabler_atime": DrRoles.add_time.field_name,
}


class DrUserRole(models.Model):
    """
    用户角色关系
    """
    id = models.CharField(verbose_name='id', max_length=40, primary_key=True, db_column='id')
    user_id = models.CharField(verbose_name='用户id', max_length=40, blank=True)
    role_id = models.CharField(verbose_name='角色id', max_length=10, blank=True)

    class Meta:
        db_table = "dr_user_roles"


SQL_DIC_USERROLE = {
    "table3": DrUserRole._meta.db_table,
    "table3_id": DrUserRole.id.field_name,
    "table3_uid": DrUserRole.user_id.field_name,
    "table3_rid": DrUserRole.role_id.field_name,
}


class DrUserOpenId(models.Model):
    """
    用户的opendId，区分不同appId
    """
    user_id = models.CharField(verbose_name='用户id', max_length=40)
    app_id = models.CharField(verbose_name='appId', max_length=40)
    open_id = models.CharField(verbose_name='用户openId', max_length=40, blank=True)

    class Meta:
        db_table = "dr_user_openid"
        unique_together = ("user_id", "app_id")


SQL_DIC_USEROPENID = {
    "tableo": DrUserOpenId._meta.db_table,
    "tableo_uid": DrUserOpenId.user_id.field_name,
    "tableo_aid": DrUserOpenId.app_id.field_name,
    "tableo_oid": DrUserOpenId.open_id.field_name,
}

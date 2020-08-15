#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/8/30
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   blog相关

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/8/30 14:53   fls        1.0         create
"""

from django.db import models


# Create your models here.

# python manage.py makemigrations
# python manage.py migrate

class BlogParam(models.Model):
    """
    blog的参数
    """
    param_code = models.CharField(verbose_name='code', max_length=30, primary_key=True, db_column='param_code')
    param_name = models.TextField(verbose_name="名称", blank=True)
    param_value = models.TextField(verbose_name="参数值", blank=True, null=True)
    param_notes = models.TextField(verbose_name="备注", blank=True, null=True)

    class Meta:
        db_table = "blog_param"


class BlogType(models.Model):
    """
    blog的type枚举
    """
    BLOG_TYPE = (
        ('fx', '分享'), ('zz', '转载'), ('bj', '笔记'), ('gw', '感悟')
    )

    type_id = models.CharField(verbose_name='type_id', max_length=2, primary_key=True, db_column='type_id')
    type_name = models.CharField(verbose_name="类别", choices=BLOG_TYPE, max_length=10, blank=True, db_index=True)

    class Meta:
        db_table = "blog_type"


class BlogContent(models.Model):
    """
    blog内容记录表
    """
    id = models.CharField(verbose_name='id', max_length=40, primary_key=True, db_column='id')
    title = models.CharField(verbose_name="标题", max_length=50, db_column='title', blank=True, db_index=True)
    title_notes = models.CharField(verbose_name="摘要描述", max_length=100, blank=True, null=True)
    blog_type = models.CharField(verbose_name="类别", max_length=2, blank=True, db_index=True)
    blog_tags = models.TextField(verbose_name="标签", blank=True, db_index=True)
    content = models.TextField(verbose_name="内容", blank=True)
    # 0.公开;后期考虑结合用户的level，如：未登录则默认用户level=0，可以查看read_level<=0的数据;登录后的用户level=n，可以查看read_level<=n的数据
    read_level = models.IntegerField(verbose_name="阅读级别", default=0)
    read_cnt = models.IntegerField(verbose_name="阅读量", default=0)
    bg_url = models.TextField(verbose_name="背景图", blank=True, null=True)
    auth_account = models.CharField(verbose_name="作者用户名", max_length=50, blank=True)
    auth_name = models.CharField(verbose_name="作者姓名", max_length=50, blank=True)
    upd_account = models.CharField(verbose_name="更新人用户名", max_length=50, blank=True)
    upd_name = models.CharField(verbose_name="更新人姓名", max_length=50, blank=True)
    add_time = models.DateTimeField(verbose_name="添加时间", blank=True, null=True)
    upd_time = models.DateTimeField(verbose_name="修改时间", blank=True, null=True)

    class Meta:
        db_table = "blog_content"


class BlogContentComment(models.Model):
    """
    blog内容评论记录
    """
    id = models.CharField(verbose_name='id', max_length=40, primary_key=True, db_column='id')
    blog_id = models.CharField(verbose_name="blog的id", max_length=40, db_index=True)
    user_id = models.CharField(verbose_name="用户id", max_length=40, db_index=True, blank=True, null=True)
    user_account = models.CharField(verbose_name="用户名", max_length=50, blank=True, null=True)
    user_name = models.CharField(verbose_name="姓名", max_length=50, blank=True, null=True)

    is_del = models.CharField(verbose_name="是否被删除", max_length=1, db_index=True)
    add_time = models.DateTimeField(verbose_name="添加时间", blank=True, null=True)

    class Meta:
        db_table = "blog_content_comment"


SQL_DIC_TYPE = {
    "table2": BlogType._meta.db_table,
    "table2_type_name": BlogType.type_name.field_name,
    "table2_type_id": BlogType.type_id.field_name,
}
sql_dic1 = {"table1": BlogContent._meta.db_table,
            "table1_id": BlogContent.id.field_name,
            "table1_title": BlogContent.title.field_name,
            "table1_tags": BlogContent.blog_tags.field_name,
            "table1_notes": BlogContent.title_notes.field_name,
            "table1_type_id": BlogContent.blog_type.field_name,
            "table1_aacc": BlogContent.auth_account.field_name,
            "table1_aname": BlogContent.auth_name.field_name,
            "table1_atime": BlogContent.add_time.field_name,
            "table1_rcnt": BlogContent.read_cnt.field_name,
            "table1_rlevel": BlogContent.read_level.field_name,
            "table1_content": BlogContent.content.field_name,
            "table1_bgurl": BlogContent.bg_url.field_name,
            "table1_uacc": BlogContent.upd_account.field_name,
            "table1_uname": BlogContent.upd_name.field_name,
            }
SQL_DIC_PARAM = {
    "table1": BlogParam._meta.db_table,
    "table1_code": BlogParam.param_code.field_name,
    "table1_value": BlogParam.param_value.field_name,
}
SQL_DIC_BLOG = {**sql_dic1, **SQL_DIC_TYPE}

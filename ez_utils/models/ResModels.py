#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/8/30
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-models:公共返回值类

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/8/30 19:53   fls        1.0         create
"""


class ResCode:
    def __init__(self):
        # 业务成功
        self.succ = 0
        # 业务失败
        self.fail = 1
        # 需要登录(token无效等)
        self.need_login = 8
        # 异常
        self.err = 9


class ResModel:
    """
    通用返回值结构
    """

    def __init__(self, code=None, msg=None, data=None):
        self.ResCode = ResCode()
        self.code = code or self.ResCode.fail
        self.msg = msg or "操作失败"
        self.data = data or {}

    def to_dic(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }


class ResPageModel(ResModel):
    """
    通用返回值结构-含分页
    """

    def __init__(self, code=None, msg=None,
                 page=None, rsCount=None, limit=None,
                 data=None):
        self.ResCode = ResCode()
        self.code = code or self.ResCode.fail
        self.msg = msg or "操作失败"
        self.data = data or []
        self.page, self.rsCount, self.limit = page, rsCount, limit
        self.pageCount = 0

    def to_dic(self):
        """
        分页相关数据计算
        :return:
        """
        self.page = int(self.page or 0)
        self.rsCount = self.rsCount or 0
        self.limit = int(self.limit or 10)
        self.pageCount = int(self.rsCount / self.limit) if self.rsCount % self.limit == 0 else int(
            self.rsCount / self.limit) + 1
        self.data = {"list": self.data,
                     "page": self.page, "limit": self.limit, "count": self.rsCount,
                     "pageCount": self.pageCount}
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }

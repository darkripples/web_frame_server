#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/08/30
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-models:公共返回值类

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/08/30 19:53   fls        1.0         create
2019/11/30 10:17   fls        1.1         增加400、404、500的返回值
"""


class ResCode:
    def __init__(self):
        # 业务成功
        self.succ = 0
        # 业务失败
        self.fail = 1
        # 请求资源不存在
        self.err_404 = 2
        # 请求参数不合法
        self.err_400 = 3
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


class ResModelToLogin(ResModel):
    """
    通用返回值-访问某资源需登录
    """

    def __init__(self):
        self.ResCode = ResCode()
        self.code = self.ResCode.need_login
        self.msg = "请登录后访问"
        self.data = {}


class ResModel404(ResModel):
    """
    通用返回值-定义404状态的返回值
    """

    def __init__(self):
        self.ResCode = ResCode()
        self.code = self.ResCode.err_404
        self.msg = "请求的资源不存在"
        self.data = {}


class ResModel400(ResModel):
    """
    通用返回值-定义400状态的返回值
    """

    def __init__(self):
        self.ResCode = ResCode()
        self.code = self.ResCode.err_400
        self.msg = "请求的参数不合法"
        self.data = {}


class ResModel500(ResModel):
    """
    通用返回值-定义500状态的返回值
    """

    def __init__(self):
        self.ResCode = ResCode()
        self.code = self.ResCode.err
        self.msg = "系统应用异常"
        self.data = {}


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

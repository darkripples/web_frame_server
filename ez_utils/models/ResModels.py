# coding:utf8

"""
# @Time : 2019/8/30 19:53
# @Author : fls
# @Desc: 返回值类
"""


class ResCode:
    def __init__(self):
        # 业务成功
        self.succ = 0
        # 业务失败
        self.fail = 1
        # 异常
        self.err = 9


class ResModel:
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
    def __init__(self, code=None, msg=None,
                 page=None, rsCount=None, limit=None,
                 data=None):
        self.ResCode = ResCode()
        self.code = code or self.ResCode.fail
        self.msg = msg or "操作失败"
        self.data = data or []
        self.page = page
        self.rsCount = rsCount
        self.limit = limit

    def to_dic(self):
        self.page = 0 if self.page == None else int(self.page)
        self.rsCount = 0 if self.rsCount == None else self.rsCount
        self.limit = int(self.limit or 10)
        self.pageCount = int(self.rsCount / self.limit) if self.rsCount % self.limit == 0 else int(
            self.rsCount / self.limit) + 1
        self.data = {"list": self.data or [],
                     "page": self.page, "limit": self.limit, "count": self.rsCount,
                     "pageCount": self.pageCount}
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }

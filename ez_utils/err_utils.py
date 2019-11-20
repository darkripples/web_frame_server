# coding:utf8

"""
# @Time : 2019/8/30 23:12 
# @Author : fls
# @Desc: 定义异常信息
"""

import os
import traceback

from ez_utils import fls_log


def err_check(f):
    """
    异常捕获装饰器-无返回值
    :param f:
    :return:
    """

    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            flog = fls_log(handler_name="")
            flog.log_error(os.path.relpath(f.__globals__['__file__']) + "." + f.__name__, traceback.format_exc())
            return None

    return wrapper

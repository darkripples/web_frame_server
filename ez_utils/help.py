#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2016/06/06
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-打印帮助信息

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2016/06/06 11:41   fls        1.0         create
"""

from .attrdict import help as attrdict_help
from .fmt_utils import help as fmt_help
from .date_utils import help as date_help
from .file_utils import help as file_help


def help():
    print("========FLS工具类==工具说明=起=========")
    attrdict_help("①")
    fmt_help("②")
    date_help("③")
    file_help("④")
    print("========FLS工具类==工具说明=止=========")

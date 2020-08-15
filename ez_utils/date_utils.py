#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2018/10/31
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-日期相关utils

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2018/10/31 11:41   fls        1.0         create
2020/08/01 11:43   fls        1.1         新增函数get_current_week
"""

import datetime

FMT_DATETIME = '%Y%m%d%H%M%S'
FMT_DATETIME_SEPARATE = '%Y-%m-%d %H:%M:%S'
FMT_DATE = '%Y%m%d'
FMT_TIME = '%H%M%S'


def fmt_date(date=None, fmt=FMT_DATETIME_SEPARATE):
    """格式化日期(date = datetime.datetime.now(), fmt = '%Y-%m-%d %H:%M:%S')
    \t\t@param: date 日期,为空则取当前日期
    \t\t@param: fmt 格式化样式
    """
    if not date:
        date = datetime.datetime.now()
    n = date.strftime(fmt)
    return n


def str2date(date=None, fmt=FMT_DATETIME_SEPARATE):
    """
    字符串转日期时间格式
    :param date:
    :param fmt:
    :return:
    """
    if not date:
        return fmt_date(date=None, fmt=fmt)
    return datetime.datetime.strptime(date, fmt)


def get_day_n(date=None, day=1, fmt=FMT_DATETIME_SEPARATE):
    """获取n天后或-n天前的日期(date = datetime.datetime.now(), day = 1, fmt = '%Y-%m-%d %H:%M:%S')
    \t\t@param: date 日期,为空则取当前日期
    \t\t@param: day n天后的日期,默认1天后,为负数则取n天前的日期
    \t\t@param: fmt 格式化样式
    """
    if not date:
        date = datetime.datetime.now()
    return fmt_date(date=date + datetime.timedelta(days=day), fmt=fmt)


def get_seconds_n(date=None, seconds=0, fmt=FMT_DATETIME_SEPARATE):
    """获取n秒后或-n秒前的日期(date = datetime.datetime.now(), seconds = 1, fmt = '%Y-%m-%d %H:%M:%S')
    \t\t@param: date 日期,为空则取当前日期
    \t\t@param: seconds n秒后的时间,默认0秒后,为负数则取n秒前的时间
    \t\t@param: fmt 格式化样式
    """
    if not date:
        date = datetime.datetime.now()
    return fmt_date(date=date + datetime.timedelta(seconds=seconds), fmt=fmt)


def get_interval_day(start, end, fmt=FMT_DATE):
    """获取日期间的天数(start, end, fmt = '%Y%m%d')
    \t\t@param: start 开始日期
    \t\t@param: end 结束日期
    \t\t@param: fmt 格式化样式
    """

    def gen_dates(b_date, days):
        day = datetime.timedelta(days=1)
        for i in range(days):
            yield b_date + day * i

    if start is None:
        return []
    start = datetime.datetime.strptime(start, fmt)
    if end is None:
        end = datetime.datetime.now()
    else:
        end = datetime.datetime.strptime(end, fmt)
    data = []
    for d in gen_dates(start, (end - start).days + 1):
        data.append(d.strftime(fmt))
    return data


def reformat_date_str(rq1, fmt1, fmt2):
    """按目标格式，重新格式化日期(rq1, fmt1, fmt2)
    \t\t@param: rq1 开始日期
    \t\t@param: fmt1 rq1的格式
    \t\t@param: fmt2 目标格式
    """
    return datetime.datetime.strptime(rq1, fmt1).strftime(fmt2)


def get_current_week(date=None, fmt=FMT_DATE):
    """
    返回日期所在周的日期字符串列表
    :param date:
    :param fmt:
    :return:
    """
    if not date:
        date = datetime.datetime.now()
    monday = date
    one_day = datetime.timedelta(days=1)
    while monday.weekday() != 0:
        monday -= one_day

    # 返回所在周的字符串列表
    ret = []
    for i in range(7):
        ret.append((monday + datetime.timedelta(days=i)).strftime(fmt))

    return ret


def help(num='①'):
    print(num + "关于日期时间")
    print("\tfmt_date(date = datetime.datetime.now(), fmt = '%Y-%m-%d %H:%M:%S')")
    print("\t" + fmt_date.__doc__)
    print("\tafter_date(date = datetime.datetime.now(), day = 1, fmt = '%Y-%m-%d %H:%M:%S)")
    print("\t" + get_day_n.__doc__)
    print("\tafterSeconds(date = datetime.datetime.now(), seconds = 0, fmt = '%Y-%m-%d %H:%M:%S)")
    print("\t" + get_seconds_n.__doc__)
    print("\tinterval_day(start, end, fmt = '%Y%m%d')")
    print("\t" + get_interval_day.__doc__)
    print("\treformat_date_str(rq1, fmt1, fmt2)")
    print("\t" + reformat_date_str.__doc__)

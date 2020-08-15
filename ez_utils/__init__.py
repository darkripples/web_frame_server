#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2018/10/31
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2018/10/31 11:41   fls        1.0.0         create
2020/08/01 11:43   fls        1.0.1         新增函数get_current_week
2020/08/14 11:40   fls        1.1           规范下划线转驼峰func命名、新增驼峰转下划线func命名
"""
version = "1.0.2"

from .fls_log import log_func

flog = log_func()

from .attrdict import AttrDict as fdic
from .fmt_utils import fmt_null_obj as fnull, e_string as fstr, e_int, e_int_money, hump2underline
from .date_utils import (fmt_date as fmt_date, get_day_n as after_date, get_seconds_n as after_seconds,
                         get_interval_day as interval_day, reformat_date_str as reformat_date_str,
                         str2date as str2date, get_current_week)
from .date_utils import FMT_DATETIME, FMT_DATE, FMT_TIME, FMT_DATETIME_SEPARATE
from .file_utils import read_in_chunks as read_file, get_file_size, file_del
from .dbpool import connection, sql_execute
from .err_utils import err_check, params_verify, ParamsVerifyError
from .http_utils import get_ip, match_url
from .position_utils import ip2jwd, is_internal_ip, ip2city
from .file_utils import walk_dir, glob_dir
from .read_conf_utils import read_conf
from .pwd_utils import PwdCtrl
from .redis_utils import RedisCtrl
from .verify_code_utils import ValidCodeImg
from .sms_utils import sms_send
from .email_utils import email_send
#from .block_chain_utils import BlockChain
from .faker_utils import FakerObj

from .help import help

#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2016/06/07
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-log记录相关

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2016/06/07 11:41   fls        1.0         create
2019/10/24         fls        2.0         重构
2019/11/20         fls        2.1         优化 无handler_name的情况
2019/12/18         fls        2.2         优化引包方式
2020/06/09         fls        3.0         参考https://www.cnblogs.com/shouke/p/10157798.html改为单例模式
"""

from threading import Lock
from logging import getLogger, Formatter, StreamHandler
from logging.handlers import TimedRotatingFileHandler
from os import path, makedirs
from .read_conf_utils import read_conf
from conf import INI_NAME


class FlsLog(object):
    def __init__(self, log_config_file):
        pass

    def __new__(cls, log_config_file):
        mutex = Lock()
        # 上锁，防止多线程下出问题
        mutex.acquire()
        if not hasattr(cls, 'instance'):
            cls.instance = super(FlsLog, cls).__new__(cls)
            # 定义log文件位置
            # 项目基准路径
            cls.instance.base_path = path.dirname(path.dirname(path.abspath(__file__)))
            # log文件路径
            file_path = path.join(cls.instance.base_path, "logs")
            if not path.exists(file_path):
                makedirs(file_path)
            # 读取配置文件
            log_config = read_conf(log_config_file).LOGGING
            cls.instance.log_filename = path.join(file_path, log_config.logger_name + '.log')
            cls.instance.fmt = log_config.fmt
            cls.instance.log_level = int(log_config.log_level)
            cls.instance.logger_name = log_config.logger_name
            cls.instance.console_log_on = int(log_config.console_log_on)
            cls.instance.logfile_log_on = int(log_config.logfile_log_on)
            cls.instance.logger = getLogger(cls.instance.logger_name)
            cls.instance.__config_logger()
        mutex.release()
        return cls.instance

    def get_logger(self):
        return self.logger

    def __config_logger(self):
        # 设置日志格式
        fmt = self.fmt.replace('|', '%')
        formatter = Formatter(fmt)

        if self.console_log_on == 1:
            # 开启控制台日志
            console = StreamHandler()
            console.setFormatter(formatter)
            self.logger.addHandler(console)

        if self.logfile_log_on == 1:
            # 开启文件日志
            rt_file_handler = TimedRotatingFileHandler(self.log_filename, when='D', interval=1, encoding="utf-8")
            rt_file_handler.setFormatter(formatter)
            # 设置bak后缀，默认的suffix为 Y-%m-%d_%H-%M-%S
            rt_file_handler.suffix = "bak.%Y%m%d%H%M%S.log"
            self.logger.addHandler(rt_file_handler)

        self.logger.setLevel(self.log_level)


def log_func():
    """
    对外提供的接口
    :return:
    """
    return FlsLog(path.join(path.dirname(path.dirname(path.abspath(__file__))), "conf", INI_NAME)).get_logger()

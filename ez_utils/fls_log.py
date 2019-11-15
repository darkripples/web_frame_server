# coding:utf8
## Some Func About 'Write Log'
## Use: flog or fls_log(log_file)
# 2016/6/7 Add fls_log()
# 2019/10/24 重构

import logging, os
from .date_utils import fmt_date, FMT_DATE


def _get_msg4log(*args):
    # Get LOG msg
    msg = ''
    try:
        if len(args) > 1:
            if "%" in args[0]:
                msg = args[0] % args[1:]
            else:
                msg = ' '.join([str(i) for i in args])
        elif len(args) == 1:
            msg = str(args[0])
        else:
            msg = ''
    except:
        pass
    return msg


class Fls_Log:
    # Write LOG
    def __init__(self, log_filepath=None, file_name=None, date_name=fmt_date(fmt=FMT_DATE)[:8],
                 handler_name='root', log_level=logging.DEBUG, show_console=True):
        if not log_filepath:
            log_filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        if not os.path.exists(log_filepath):
            os.makedirs(log_filepath)
        if not file_name:
            file_name = "darkripples"

        self.log_filepath = os.path.join(log_filepath, file_name + '.log.' + date_name)

        self.logger = logging.getLogger(handler_name)
        self.handlers = self.logger.handlers

        if not self.handlers:
            fh = logging.FileHandler(self.log_filepath, encoding="utf-8")
            ch = logging.StreamHandler()

            # 设置输出日志格式
            fmt = "%(asctime)s %(levelname)s %(message)s"
            if handler_name:
                fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
            formatter = logging.Formatter(
                fmt=fmt,
                datefmt=None
            )

            # 为handler指定输出格式
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            # 为logger添加的日志处理器
            self.logger.addHandler(fh)
            if show_console:
                self.logger.addHandler(ch)

            self.logger.setLevel(log_level)

            self.handlers = self.logger.handlers

    def log_info(self, *args):
        # Write info msg
        self.logger.info(_get_msg4log(*args))

    def log_debug(self, *args):
        # Write debug msg
        self.logger.debug(_get_msg4log(*args))

    def log_warning(self, *args):
        # Write warning msg
        self.logger.warning(_get_msg4log(*args))

    def log_error(self, *args):
        # Write error msg
        self.logger.error(_get_msg4log(*args))


def fls_log(log_filepath=None, file_name='darkripples', handler_name='root', show_console=True):
    return Fls_Log(log_filepath=log_filepath, file_name=file_name, handler_name=handler_name, show_console=show_console)


if __name__ == '__main__':
    # For test:
    a = fls_log()
    a.log_info('11212')
    a.log_debug('x')
    a.log_warning('11212')
    a.log_error('error:%s', 'test')

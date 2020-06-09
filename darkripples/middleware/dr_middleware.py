#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/11/15
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   darkripples-中间件

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/11/15 14:24   fls        1.0         create
"""

import traceback
from jwt.exceptions import PyJWTError

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.apps import apps

from ez_utils import flog, match_url
from ez_utils.models import ResModel


def check_token(req_token):
    """
    校验token
    :param req_token:
    :return:
    """
    if not req_token:
        ret = ResModel()
        ret.code = ret.ResCode.need_login
        ret.msg = ""
        return JsonResponse(ret.to_dic())
    from rest_framework_jwt.settings import api_settings
    jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
    try:
        # {'user_id': 'a', 'username': 'fls',}
        jwt_decode_handler(req_token)
    except:
        ret = ResModel()
        ret.code = ret.ResCode.need_login
        ret.msg = "无效的token"
        return JsonResponse(ret.to_dic())
    return None


class DRMiddleware(MiddlewareMixin):
    """
    中间件类
    """

    def process_request(self, request):
        """
        请求前调用，不可return
        :param request:
        """
        print('>>>>process_request>>>>>>')
        # request.META['DR_PAR1'] = 9
        # 请求路径.如/app_dr/index/
        fpath = request.get_full_path()
        need_check_token = False
        for c in apps.get_app_configs():
            if not c.name.startswith('app_'):
                continue
            if 'check_token_url_list' not in dir(c):
                continue
            for check_u in c.check_token_url_list:
                # todo 匹配方式需再详尽测试
                if match_url(fpath, check_u):
                    need_check_token = True
                    break

        if need_check_token:
            # 校验token
            req_token = request.META.get('HTTP_TOKEN')
            ret_check = check_token(req_token)
            if ret_check is not None:
                return ret_check

    def process_response(self, request, response):
        """
        view处理后调用，必须return
        若有process_exception，则走完异常处理后再来到此处
        :param request:
        :param response:
        :return:
        """
        return response

    def process_exception(self, request, exception):
        """
        视图函数发生异常时调用
        :param request:
        :param exception:
        :return:
        """
        flog.log_error(traceback.format_exc())
        print('>>>>>>process_exception>>>>>>>', exception, "|", type(exception))

        # 默认返回值Response
        ret = ResModel()
        ret.code = ret.ResCode.err
        ret.msg = "系统应用异常"

        if isinstance(exception, PyJWTError):
            # jwt校验token无效,不在具体区分详细的异常类型了
            ret.code = ret.ResCode.need_login
            ret.msg = "TOKEN无效"

        return JsonResponse(ret.to_dic())

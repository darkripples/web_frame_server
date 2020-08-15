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
2019/11/30 10:20   fls        1.1         把异常处理提取到views_err.py中
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.apps import apps

from ez_utils import match_url
from ez_utils.models import ResModelToLogin

from app_dr.dr_utils import check_token, upd_token_exp


class DRMiddleware(MiddlewareMixin):
    """
    中间件类
    """

    def process_request(self, request):
        """
        请求前调用，不可return
        :param request:
        """
        # 主动要求校验token
        needtoken = request.GET.get('needtoken')
        need_check_token = False
        if not needtoken:
            # 请求路径.如/app_dr/index/
            fpath = request.get_full_path()
            for c in apps.get_app_configs():
                if not c.name.startswith('app_'):
                    continue
                if 'check_token_url_list' not in dir(c):
                    continue
                for check_u in c.check_token_url_list:
                    # 匹配方式需再详尽测试
                    if match_url(fpath, check_u):
                        need_check_token = True
                        break
        else:
            need_check_token = True

        if need_check_token:
            # 校验token
            req_token = request.META.get('HTTP_TOKEN')
            ret_info, user_info = check_token(req_token)
            if ret_info is not None:
                ret = ResModelToLogin()
                ret.msg = ret_info
                return JsonResponse(ret.to_dic())
            # 需更新token过期时间
            upd_token_exp(req_token)
            request.META["USER_ID"] = user_info["id"]

    def process_response(self, request, response):
        """
        view处理后调用，必须return
        若有process_exception，则走完异常处理后再来到此处
        :param request:
        :param response:
        :return:
        """
        # 判断同一请求频繁程度 todo
        return response

    def process_exception(self, request, exception):
        """
        视图函数发生异常时调用
        :param request:
        :param exception:
        :return:
        """
        from app_dr.views_err import handler_500
        return handler_500(exception, req=request)

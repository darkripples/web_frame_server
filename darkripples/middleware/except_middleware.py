# coding:utf8

import traceback

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

from ez_utils import fls_log
from ez_utils.models import ResModel

flog = fls_log(handler_name="")


class ExceptMiddleware(MiddlewareMixin):
    """
    中间件类
    """

    def process_request(self, request):
        """
        请求前调用，不可return
        :param request:
        """
        pass

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
        ret = ResModel()
        ret.code = ret.ResCode.err
        ret.msg = "系统应用异常"
        return JsonResponse(ret.to_dic())

# !/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/11/28
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-短信发送相关utils

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/11/28 17:28     fls        1.0         create
"""

import json

from ez_utils import flog
from conf import ALI_ACCESS_KEY, ALI_SECRET_KEY, ALI_SMS_SIGN_NAME


def sms_send(phones, par_dic, tmpl_code, sms_type):
    """
    通用短信发送
    :param phones: 可逗号分隔
    :param par_dic:
    :param tmpl_code: 短信模板代码
    :param sms_type: 短信类型，记录日志使用
    :return:
    """
    if not phones:
        return "请填入收信手机号"

    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.request import CommonRequest

    client = AcsClient(ALI_ACCESS_KEY, ALI_SECRET_KEY, 'cn-hangzhou')

    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('RegionId', "cn-hangzhou")
    request.add_query_param('PhoneNumbers', phones)
    request.add_query_param('SignName', ALI_SMS_SIGN_NAME)
    request.add_query_param('TemplateCode', tmpl_code)
    request.add_query_param('TemplateParam', json.dumps(par_dic))

    response = client.do_action_with_exception(request)

    flog.info(f"短信发送.{sms_type}|response:{response}|phones:{phones}")
    return response

#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/09/02
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   darkripples总平台相关-通用views

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/09/02 11:41   fls        1.0         create
2019/11/22 10:27   fls        1.1         加入djangorestframework-jwt相关，并初始化测试代码
2019/11/29 15:51   fls        2.0         去除测试代码，增加通用文件上传api
"""

from os import path, makedirs
from uuid import uuid1
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ez_utils.models import ResModel
from ez_utils import fmt_date, FMT_DATE, get_ip
from app_dr.dr_utils import req_invalid_check


@csrf_exempt
def index(req):
    """
    2017/05/29 fls
    frist coming
    """
    ret = ResModel()
    ret.msg = '欢迎dr.' + get_ip(req)
    ret.code = ret.ResCode.succ
    return JsonResponse(ret.to_dic())


@require_POST
@csrf_exempt
def upload_file(req):
    """
    文件上传
    :param req: pathPre,file
    :return:
    """
    ret = ResModel()
    ret.msg = req_invalid_check(req)
    if ret.msg:
        # 请求合法性校验不通过
        return JsonResponse(ret.to_dic())

    file_obj = req.FILES.get('file')
    if not file_obj:
        ret.msg = '未选择文件'
        return JsonResponse(ret.to_dic())

    # 允许指定类型前缀，以区分不同业务
    path_pre = req.POST.get('pathPre', '')
    # 上传路径
    up_path_pre = settings.UPLOAD_DIR
    # 按日期年月分组
    now_date = fmt_date(fmt=FMT_DATE)
    up_path = path.join(up_path_pre, path_pre, now_date)
    if not path.exists(up_path):
        makedirs(up_path)

    # 重命名，防止重名
    file_type = path.splitext(file_obj.name)[1]
    file_name = str(uuid1()).replace('-', '') + file_type
    # 保存文件
    with open(path.join(up_path, file_name), 'wb') as fp:
        for chunk in file_obj.chunks():
            fp.write(chunk)
    ret.msg = '已上传'
    ret.code = ret.ResCode.succ
    # fileSize单位是字节.fileSize/1024单位即kb；fileSize/1024/1024单位即mb
    ret.data = {"oldName": file_obj.name,
                "newName": path.join(settings.STATIC_ROOT, settings.UPLOAD_ROOT, path_pre, now_date, file_name),
                "fileType": file_type.split(".")[-1], "fileSize": file_obj.size}
    return JsonResponse(ret.to_dic())

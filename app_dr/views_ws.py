#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2020/04/18
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   websocket
    > type:
        init:   连接后响应
        sign:   客户端报告自己身份
        return: 原样返回

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/04/18 11:00   fls        1.0         create
"""

from threading import RLock
from json import dumps, loads
from ez_utils.models import ResModel
from ez_utils import flog
from dwebsocket.decorators import accept_websocket
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


# 记录当前websocket对象
WS_OBJ = set()


@accept_websocket
def wsocket_init(req):
    """
    websocket连接初始化
    https://blog.csdn.net/xianailili/article/details/82180114
    :param req:
    :return:
    """
    ret = ResModel()
    ret.code = ret.ResCode.succ
    ret.msg = ""

    if req.is_websocket():
        # rlock线程锁
        lock = RLock()
        try:
            # 抢占资源
            lock.acquire()

            global WS_OBJ
            w_obj = req.websocket
            WS_OBJ.add(w_obj)

            ret.data = {"nowCnt": len(WS_OBJ), "type": "init"}
            ret_final = dumps(ret.to_dic(), ensure_ascii=False).encode('utf-8')
            w_obj.send(ret_final)
            for m in w_obj:
                if not m:
                    break
                print('客户端消息:', m.decode('utf-8'))
                ret.data = {"nowCnt": len(WS_OBJ), "clientMsg": m.decode('utf-8'), "type": "return"}
                ret_final = dumps(ret.to_dic(), ensure_ascii=False).encode('utf-8')
                w_obj.send(ret_final)
        except:
            pass
        finally:
            # 移除当前在线的websocket对象
            WS_OBJ.remove(w_obj)
            # 释放锁
            lock.release()


def websocket_send_all(msg_dic):
    """
    发送消息-全体
    :param msg_dic:
    :return:
    """
    ret_final = dumps(msg_dic, ensure_ascii=False).encode('utf-8')
    # 遍历
    for cli in WS_OBJ:
        cli.send(ret_final)
    flog.debug("ws消息广播[%s]:%s" % (len(WS_OBJ), str(msg_dic)))


@csrf_exempt
def api_websocket_msg(req):
    """
    发送消息-api
    :param req:
    :return:
    """
    ret = ResModel()
    ret.code = ret.ResCode.succ
    ret.msg = ""
    data = loads(req.POST.get("data", "{}"))

    ret.data = {"nowCnt": len(WS_OBJ), "type": "yw", "data": data}
    ret_final = ret.to_dic()
    websocket_send_all(ret_final)
    return JsonResponse(ret_final)

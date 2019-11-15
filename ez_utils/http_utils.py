# coding:utf8

"""
# @Time : 2019/9/14 21:48 
# @Author : fls
# @Desc: http相关的utils
"""


def get_ip(request):
    """
    获取请求者ip
    :param request:
    :return:
    """
    # X-Forwarded-For:简称XFF头，它代表客户端，也就是HTTP的请求端真实的IP，
    # 只有在通过了HTTP 代理或者负载均衡服务器时才会添加该项。
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # 所以这里是真实的ip
        ip = x_forwarded_for.split(',')[0]
    else:
        # 这里获得代理ip
        ip = request.META.get('REMOTE_ADDR')
    return ip

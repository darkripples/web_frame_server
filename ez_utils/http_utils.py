# !/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/09/14
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-http相关

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/09/14 21:48    fls        1.0         create
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


def match_url(aim_url, role_str):
    """

    :param aim_url:
    :param role_str:
    :return:
    """
    from re import match
    rs = match(role_str, aim_url)
    return rs.span() if rs else None


if __name__ == "__main__":
    print(match_url("/app_dr/index/", "/app_dr/*"))
    print(match_url("/app_dr/index/", "/app_dr/index/"))
    print(match_url("/app_dr/index/", "/*"))

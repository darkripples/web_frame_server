#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/09/02
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-AI聊天相关utils:腾讯AI聊天机器人

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/09/02 22:08   fls        1.0         create
"""

import requests
from .md5sign import get_params


def get_content(plus_item):
    # 聊天的API地址
    url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat"
    # 获取请求参数
    plus_item = plus_item.encode('utf-8')
    payload = get_params(plus_item)
    r = requests.post(url, data=payload)
    return r.json()["data"]["answer"]


if __name__ == '__main__':
    while True:
        comment = input('我：')
        if comment == 'q':
            break
        if comment.strip() == '':
            continue
        answer = get_content(comment)
        print('机器人：' + answer)

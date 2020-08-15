# !/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/11/23
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-密码相关utils

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/11/23 15:09     fls        1.0         create
"""


class PwdCtrl:
    """
    password controller
    """

    def __init__(self):
        """
        初始化
        """
        self.salt = ''

    def get_salt(self, salt_length=8):
        """
        获取盐值
        :return:
        """
        from random import Random
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        # 获取chars的最大下标
        len_chars = len(chars) - 1
        random = Random()
        for i in range(salt_length):
            # 每次随机从chars中抽取一位,拼接成一个salt值
            self.salt += chars[random.randint(0, len_chars)]
        return self.salt

    def create_md5(self, src_str=None, salt=None):
        """
        创建md5摘要
        :param src_str:
        :param salt:
        :return:
        """
        from hashlib import md5
        md5_obj = md5()
        md5_obj.update(((salt or self.salt) + (src_str or '')).encode('utf-8'))
        return md5_obj.hexdigest().upper()


if __name__ == '__main__':
    f = PwdCtrl()
    print(f.get_salt())
    print(f.create_md5("123456"))

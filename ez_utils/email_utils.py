#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/11/28
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-email相关utils

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/11/28 17:28   fls        1.0         create
"""

import smtplib
from os import path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr
from conf import (EMAIL_HOST_SENDER, EMAIL_HOST_PASSWORD, EMAIL_HOST_SMTP, EMAIL_HOST_PORT, EMAIL_HOST_USER,
                  EMAIL_HOST_SENDNAME)


class SendEmail(object):
    """
    smtp邮件功能封装
    """

    def __init__(self, host: str = '', user: str = '', password: str = '', port: int = 465, sender: str = '',
                 sender_name: str = 'DarkRipples', receive: list = None):
        """
        :param host: 邮箱服务器地址
        :param user: 登陆用户名
        :param password: 登陆密码
        :param port: 邮箱服务端口
        :param sender: 邮件发送者
        :param receive: 邮件接收者
        :param sender_name: 发件人姓名
        """
        self.HOST = host
        self.USER = user
        self.PASSWORD = password
        self.PORT = port
        self.SENDER = sender
        self.RECEIVE = receive
        self.SENDER_NAME = sender_name

        # 与邮箱服务器的连接
        self._server = ''
        # 邮件对象,用于构造邮件内容
        self._email_obj = ''

    def connect_smtp_server(self, method='default'):
        """连接到smtp服务器"""
        if method == 'default':
            self._server = smtplib.SMTP(self.HOST, self.PORT, timeout=2)
        if method == 'ssl':
            self._server = smtplib.SMTP_SSL(self.HOST, self.PORT, timeout=2)

        self._server.login(self.USER, self.PASSWORD)

    def _format_addr(self, s):
        """
        构造邮件收/发件人信息
        :param s:
        :return:
        """
        name, addr = parseaddr(s)
        return formataddr(
            (Header(name, 'utf-8').encode(), addr)
        )

    def construct_email_obj(self, subject='null email'):
        """构造邮件对象
        subject: 邮件主题
        from: 邮件发送方
        to: 邮件接收方
        """

        # mixed参数表示混合类型，这个邮件对象可以添加html,txt,附件等内容
        msg = MIMEMultipart('mixed')
        msg['Subject'] = subject
        msg['From'] = self._format_addr(self.SENDER_NAME + " " + self.SENDER)
        msg['To'] = ';'.join(self.RECEIVE)
        self._email_obj = msg

    def add_content(self, content: str, _type: str = 'txt'):
        """给邮件对象添加正文内容"""
        if _type == 'txt':
            text = MIMEText(content, 'plain', 'utf-8')
        if _type == 'html':
            text = MIMEText(content, 'html', 'utf-8')

        self._email_obj.attach(text)

    def add_file(self, file_path: str):
        """
        给邮件对象添加附件
        :param file_path: 文件路径
        :return: None
        """
        # 构造附件1，传送当前目录下的 test.txt 文件
        email_file = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
        email_file["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        file_name = path.basename(file_path)
        email_file["Content-Disposition"] = f'attachment; filename="{file_name}"'
        self._email_obj.attach(email_file)

    def send_email(self):
        """发送邮件"""
        # 使用send_message方法而不是sendmail,避免编码问题
        self._server.send_message(from_addr=self.SENDER, to_addrs=self.RECEIVE, msg=self._email_obj)

    def quit(self):
        self._server.quit()

    def close(self):
        self._server.close()


def email_send(receivers, title, content):
    """
    对外api
    :param receivers
    :param title:
    :param content:
    :return:
    """
    if not receivers or not receivers[0]:
        return '收件人不存在'
    email_obj = SendEmail(host=EMAIL_HOST_SMTP, user=EMAIL_HOST_USER, password=EMAIL_HOST_PASSWORD,
                          port=EMAIL_HOST_PORT, sender=EMAIL_HOST_SENDER, sender_name=EMAIL_HOST_SENDNAME,
                          receive=receivers)
    email_obj.connect_smtp_server(method='ssl')
    email_obj.construct_email_obj(subject=title)
    email_obj.add_content(content=content, _type='html')
    ret = email_obj.send_email()
    email_obj.close()
    return ret


if __name__ == '__main__':
    from conf import EMAIL_REG_TITLE, EMAIL_REG_CONT_CODE

    email_msg = """xxx,11:
            123456:112
                ---ddd"""
    email_send(["fls@darkripples.com"], EMAIL_REG_TITLE, EMAIL_REG_CONT_CODE % 123456)

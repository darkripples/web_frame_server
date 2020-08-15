# !/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/11/23
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-验证码相关utils

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/11/23 17:13     fls        1.0         create
"""

from os import path
from base64 import b64encode
from random import randint, Random
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

BASE_DIR = path.dirname(path.abspath(__file__))


class ValidCodeImg:
    def __init__(self, width=150, height=30, code_count=5, font_size=32, point_count=20, line_count=3,
                 img_format='png'):
        """
        可以生成一个经过降噪后的随机验证码的图片
        :param width: 图片宽度 单位px
        :param height: 图片高度 单位px
        :param code_count: 验证码个数
        :param font_size: 字体大小
        :param point_count: 噪点个数
        :param line_count: 划线个数
        :param img_format: 图片格式
        :return
        """
        self.width = width
        self.height = height
        self.code_count = code_count
        self.font_size = font_size
        self.point_count = point_count
        self.line_count = line_count
        self.img_format = img_format

    @staticmethod
    def getRandomColor():
        """获取一个随机颜色(r,g,b)格式的"""
        c1 = randint(0, 255)
        c2 = randint(0, 255)
        c3 = randint(0, 255)
        return (c1, c2, c3)

    @staticmethod
    def getRandomStr(str_length=1):
        """获取一个随机字符串，每个字符的颜色也是随机的"""
        chars = '23456789abcdefghjknpqrstuvxyz'
        # 获取chars的最大下标
        len_chars = len(chars) - 1
        random_tmp = Random()
        random_char = ''
        for i in range(str_length):
            # 每次随机从chars中抽取一位
            random_char += chars[random_tmp.randint(0, len_chars)]
        return random_char

    def getValidCodeImg(self, vcode_str=None):
        # 获取一个Image对象，参数分别是RGB模式。宽150，高30，随机颜色
        image = Image.new('RGB', (self.width, self.height), self.getRandomColor())

        # 获取一个画笔对象，将图片对象传过去
        draw = ImageDraw.Draw(image)

        # 获取一个font字体对象参数是ttf的字体文件的目录，以及字体的大小

        font = ImageFont.truetype(path.join(BASE_DIR, "vendors", "fonts", "KumoFont.ttf"), size=self.font_size)

        temp = []
        vcode_list = list(vcode_str) or [self.getRandomStr() for i_ in range(self.code_count)]
        for i in range(self.code_count):
            # 循环5次，获取5个随机字符串
            random_char = str(vcode_list[i])

            # 在图片上一次写入得到的随机字符串,参数是：定位，字符串，颜色，字体
            draw.text((10 + i * 30, -2), random_char, self.getRandomColor(), font=font)

            # 保存随机字符，以供验证用户输入的验证码是否正确时使用
            temp.append(random_char)
        valid_str = "".join(temp)

        # 噪点噪线
        # 划线
        for i in range(self.line_count):
            x1 = randint(0, self.width)
            x2 = randint(0, self.width)
            y1 = randint(0, self.height)
            y2 = randint(0, self.height)
            draw.line((x1, y1, x2, y2), fill=self.getRandomColor())

        # 画点
        for i in range(self.point_count):
            draw.point([randint(0, self.width), randint(0, self.height)], fill=self.getRandomColor())
            x = randint(0, self.width)
            y = randint(0, self.height)
            draw.arc((x, y, x + 4, y + 4), 0, 90, fill=self.getRandomColor())

        # 生成图片
        from io import BytesIO
        f = BytesIO()
        image.save(f, self.img_format)
        img_data = f.getvalue()
        base64_str = b64encode(img_data)
        f.close()
        return base64_str, valid_str


if __name__ == "__main__":
    img = ValidCodeImg(code_count=5, img_format='png')
    img_data, valid_str = img.getValidCodeImg(vcode_str='abcde')
    # 需添加前缀data:image/png;base64,
    print(valid_str)
    print(img_data)

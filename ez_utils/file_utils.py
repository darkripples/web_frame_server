#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/5/18
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-文件相关utils

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/5/18 11:41   fls        1.0         create
"""

from base64 import b64decode
from glob import glob
from os import path, walk, remove


def read_in_chunks(file_path: str, chunk_size=1024 * 1024):
    """
    Lazy function (generator) to read a file piece by piece.
    """
    file_object = open(file_path, 'rb')
    while True:
        chunk_data = file_object.read(chunk_size)
        if not chunk_data:
            break
        yield chunk_data


def walk_dir(file_path: str, include_dir=True):
    """
    loop dir
    """
    ret = []
    for root, dirs, files in walk(file_path, topdown=True):
        for name in files:
            # 文件
            ret.append(path.join(root, name))
        if include_dir:
            for name in dirs:
                # 文件夹
                ret.append(path.join(root, name))
    return ret


def glob_dir(file_path: str):
    """
    loop file
    """

    return glob(file_path)


def save_img_base64(file_path: str, img_64: str):
    """
    base64字符串保存为图片
    :param file_path: 图片保存的完整路径
    :param img_64:
    :return:
    """
    imagedata = b64decode(img_64)
    file = open(file_path, "wb")
    file.write(imagedata)
    file.close()


def get_file_size(file_path: str):
    """
    获取文件大小
    :param file_path:
    :return: 单位bytes
    """
    return path.getsize(file_path)


def file_del(file_path: str):
    """
    删除文件
    :param file_path:
    :return:
    """
    if path.exists(file_path):
        remove(file_path)
        return 0
    else:
        return 1


def help(num='①'):
    print(num + "关于文件操作")
    print("\t" + read_in_chunks.__doc__)

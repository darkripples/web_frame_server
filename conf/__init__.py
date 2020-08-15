#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/09/15
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   darkripples总平台相关

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/09/15 08:43   fls        1.0         create
"""
# 默认配置，作为base使用
from .configs_default import *

# 【当前生效的配置，开发者需按环境修改】
# from .configs_local import *

# DB for Django，放在最后
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DB_NAME,  # Or path to database file if using sqlite3.
        'USER': DB_USER,  # Not used with sqlite3.
        'PASSWORD': DB_PWD,  # Not used with sqlite3.
        'HOST': DB_HOST,  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': DB_PORT,  # Set to empty string for default. Not used with sqlite3.
    }
}

print('>载入配置:', CONFIGS_NAME)

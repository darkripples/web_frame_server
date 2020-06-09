# coding:utf8

# todo 需自己设置***的参数

# ini配置文件名
INI_NAME = 'conf.ini'

HOST = '***'
PORT = 5432
USER = '***'
PWD = '***'
DBNAME = '***'
DB_TYPE = 'postgresql'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DBNAME,  # Or path to database file if using sqlite3.
        'USER': USER,  # Not used with sqlite3.
        'PASSWORD': PWD,  # Not used with sqlite3.
        'HOST': HOST,  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': PORT,  # Set to empty string for default. Not used with sqlite3.
    }
}

SET_TITLE_CMD = "***"

# redis
REDIS_PWD = '***'
REDIS_PORT = 6379

# Email设置
EMAIL_HOST_USER = '***@darkripples.com'  # 我的邮箱帐号
EMAIL_HOST_PASSWORD = '***'  # 授权码


# 分页相关
PAGE_DEFAULT_LIMIT = 10  # 每页条数

# 防爬处理.header校验码.DR-DEBUG=校验码才行
REQ_HEADER_PWD = '***'

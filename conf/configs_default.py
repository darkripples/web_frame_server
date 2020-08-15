# coding:utf8
"""各配置参数-空白"""

CONFIGS_NAME = __file__

# ini配置文件名
INI_NAME = 'conf.ini'

# 控制台是否print sql语句
SHOW_SQL = False

# DB
DB_HOST = '127.0.0.1'
DB_PORT = 5432
DB_USER = 'postgres'
DB_PWD = 'postgres'
DB_NAME = 'darkripples'
DB_TYPE = 'postgresql'

# redis
REDIS_IP = '127.0.0.1'
REDIS_PWD = ''
REDIS_PORT = 6379
# > key前缀
REDIS_KEY_PRE_SID = 'getsid_'  # 获取sid
REDIS_KEY_PRE_SMSCODE = 'smscode_'  # 短信验证码
REDIS_KEY_PRE_EMAILCODE = 'emailcode_'  # email验证码
REDIS_KEY_PRE_SIDERR = 'errsid_'  # sid错误次数
REDIS_KEY_PRE_CODEERR = 'errsmscode_'  # 短信验证码错误次数
REDIS_KEY_PRE_PWDERR = 'errpwd_'  # 密码错误次数
REDIS_KEY_PRE_TOKEN = 'token_'  # token

# Email设置
EMAIL_HOST_SENDER = 'todo@darkripples.com'
EMAIL_HOST_SENDNAME = 'todo'
EMAIL_HOST_PASSWORD = 'todo'
EMAIL_HOST_SMTP = 'smtp.mxhichina.com'
EMAIL_HOST_PORT = 465
EMAIL_HOST_USER = 'todo@darkripples.com'

EMAIL_REG_TITLE = "【黑色涟漪】todo"
EMAIL_REG_CONT_CODE = """todo
%s
"""
EMAIL_MODPWD_TITLE = "【黑色涟漪】todo"
EMAIL_MODPWD_CONT = """todo
%s
"""
EMAIL_MODPHONE_TITLE = "【黑色涟漪】todo"
EMAIL_MODPHONE_CONT = """todo
%s
"""
EMAIL_CLOCKMSG_TITLE = "【黑色涟漪】todo"
EMAIL_CLOCKMSG_CONT = """todo
%s
"""

# 微信开发者
WECHAT_TOKEN = 'todo'

# 腾讯AI开放平台
TENCENT_AI_APP_ID = 'todo'
TENCENT_AI_APP_KEY = 'todo'

# 短网址默认页url
DWZ_DEFAULT_URL = 'd5z.fun'

# 分页相关
PAGE_DEFAULT_LIMIT = 10  # 每页条数

# 防爬处理.header校验码.DR-DEBUG=校验码才行
REQ_HEADER_PWD = 'todo'

# 七牛云 配置
QINIU_ACCESS_KEY = 'todo'
QINIU_SECRET_KEY = 'todo'
QINIU_DEFAULT_BUCKET_NAME = 'todo'

# 阿里云配置
ALI_ACCESS_KEY = 'todo'
ALI_SECRET_KEY = 'todo'
# 短信模板相关
ALI_SMS_SIGN_NAME = 'todo'
ALI_SMS_TMPL_COMMON_CODE = 'todo'  # 通用验证码
ALI_SMS_TMPL_COMMON_SIGNIN = 'todo'  # 提醒签到
ALI_SMS_TMPL_RESET_PWD = 'todo'  # 重置密码
ALI_SMS_TMPL_RESET_PHONE = 'todo'  # 更换手机号
# >短信发送号码
SMS_PHONE_SIGNIN = ['todo']  # 提醒签到

# 微信小程序
MINI_PROGRAM_APP_CONF = {'mini_1': ("appidxxxxxxxxxxxxx", "secret1111111111111"),
                         'mini_2': ("appid222222222222", "secret22222222"),
                         }

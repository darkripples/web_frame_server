#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2019/8/30
@Author     :   fls
@Contact    :   fls@darkripples.com
@Desc       :   fls易用性utils-定义异常信息相关utils

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2019/8/30 23:12    fls        1.0         create
"""

import os
import traceback

from ez_utils import fls_log


def err_check(f):
    """
    装饰器-异常捕获装饰器-无返回值
    :param f:
    :return:
    """

    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            flog = fls_log(handler_name="")
            flog.log_error(os.path.relpath(f.__globals__['__file__']) + "." + f.__name__, traceback.format_exc())
            return None

    return wrapper


class ParamsVerifyError(Exception):
    """
    异常-参数合法性校验失败
    """
    pass


def params_verify(pars_str: str):
    """
    装饰器-参数校验装饰器
    旨在校验函数调用时pars_str中的各参数不可空，逗号分隔；
    即使字典形的有默认入参的，调用时也不可省略
    * 注:1：此类调用，仍不允许
        # ---define-----
        @params_verify("a")
        def func_a(a, **kwargs)：
            pass
        # ---use-----
        # *error
        func_a('',a=1)
        # *ok
        func_a(1,b=1)
    * 注意2：未明确入参的args是无法校验的
        # ---define~1-----
        @params_verify("a")
        def func_a(*args)：
            pass
    *       下述情况，在字典形参数中允许正常校验
        # ---define~2-----
        @params_verify("a")
        def func_a(*args, **kwargs):
            pass
        # ---use-----
        # *error
        func_a(1,b=1)
        # *ok
        func_a(1,a=1)
    :param pars_str: 需校验的参数集合，逗号分隔
    :return:
    :raise: ParamsVerifyError
    """

    def check_par_(func):
        def wrapper(*args, **kwargs):
            if not pars_str:
                return func(*args, **kwargs)
            # 获取function实际的入参
            real_par_list = func.__code__.co_varnames
            # 校验校验的参数
            check_pars_list = pars_str.split(",")
            # args形参数长度
            args_length = len(args)
            # check_msg以备汇总错误信息
            check_msg = ""

            # 因为入参可以用(*args,**kwargs)或者(args1,**kwargs)或者(*args,kw1=None)等比较多变，这里要处理下
            #   a).args的长度，其实是列表形参数的真实长度；所以根据此长度，截取real_par_list中的参数
            real_args_list = real_par_list[:args_length]
            #   b).那么，这就是kwargs的内容
            # real_kwargs_list = real_par_list[args_length:]
            #   按理说，kwargs的key里是不应该有args里同名的参数的，这样就可以先判断real_args_list再查询real_kwargs_list
            #       但是，上述并不能限定住;但是按规范应该是这样的，所以不按规定的入参，抛出ParamsVerifyError异常
            #       上述，通过set后长度来判断，是否有入参重复
            if len(real_par_list) > len(set(real_par_list)):
                # 其实.这种情况python会自动拦截了，抛出异常TypeError: func_() got multiple values for argument 'a';
                # 这里冗余判断下
                raise ParamsVerifyError("function got multiple values for argument")

            # 上述校验后，可以先判断real_args_list再查询real_kwargs_list
            # 开始逐个校验
            for p in check_pars_list:
                if p in real_args_list:
                    i_real = real_args_list.index(p)
                    if args[i_real] is None or args[i_real] == "":
                        check_msg += f"参数{p}不可为空;"
                        continue
                else:
                    if kwargs.get(p) is None or kwargs.get(p) == "":
                        check_msg += f"参数{p}不可为空;"
                        continue

            if check_msg:
                # 存在校验失败的信息
                check_msg = func.__name__ + ":" + check_msg
                raise ParamsVerifyError(check_msg)

            return func(*args, **kwargs)

        return wrapper

    return check_par_

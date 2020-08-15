#!/usr/bin/env python
# coding:utf8
"""
@Time       :   2020/2/16
@Author     :   fls    
@Contact    :   fls@darkripples.com
@Desc       :   ez工具类-faker数据

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/2/16 8:16   fls        1.0         create
"""

from faker import Faker
from faker.providers import BaseProvider


class CarPlateProvider(BaseProvider):
    license_plate_provinces = (
        "京", "沪", "浙", "苏", "粤", "鲁", "晋", "冀",
        "豫", "川", "渝", "辽", "吉", "黑", "皖", "鄂",
        "津", "贵", "云", "桂", "琼", "青", "新", "藏",
        "蒙", "宁", "甘", "陕", "闽", "赣", "湘"
    )

    license_plate_last = ("挂", "学", "警", "港", "澳", "使", "领")

    license_plate_num = (
        "A", "B", "C", "D", "E", "F", "G", "H",
        "J", "K", "L", "M", "N", "P", "Q", "R",
        "S", "T", "U", "V", "W", "X", "Y", "Z",
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"
    )

    def license_plate(self):
        """ 传统车牌 """
        plate = "{0}{1}{2}".format(
            self.random_element(self.license_plate_provinces),
            self.random_uppercase_letter(),
            "".join(self.random_choices(elements=self.license_plate_num, length=5))
        )
        return plate

    def car_no(self):
        return self.license_plate()

    def special_license_plate(self):
        """ 特种车牌 """
        plate = "{0}{1}{2}{3}".format(
            self.random_element(self.license_plate_provinces),
            self.random_uppercase_letter(),
            "".join(self.random_choices(elements=self.license_plate_num, length=4)),
            self.random_element(self.license_plate_last)
        )
        return plate

    def custom_license_plate(self, prov, org, last=None):
        """
        prov: 省简称
        org: 发牌机关简称字母
        last: 特种车汉字字符
        """
        if last is None:
            plate = "{0}{1}{2}".format(prov, org,
                                       "".join(self.random_choices(elements=self.license_plate_num, length=5)))
        else:
            plate = "{0}{1}{2}{3}".format(prov, org,
                                          "".join(self.random_choices(elements=self.license_plate_num, length=4)), last)

        return plate

    def new_energy_license_plate(self, car_model=1):
        """
        新能源车牌
        car_model: 车型，0-小型车，1-大型车
        """
        plate = ""
        if car_model == 0:
            # 小型车
            plate = "{0}{1}{2}{3}{4}".format(self.random_element(self.license_plate_provinces),
                                             self.random_uppercase_letter(),
                                             self.random_element(elements=("D", "F")),
                                             self.random_element(elements=self.license_plate_num),
                                             self.random_int(1000, 9999))
        else:
            # 大型车
            plate = "{0}{1}{2}{3}".format(self.random_element(self.license_plate_provinces),
                                          self.random_uppercase_letter(),
                                          self.random_int(10000, 99999), self.random_element(elements=("D", "F")))

        return plate


class FakerObj:
    def __init__(self):
        """
        初始化
        """
        self.faker_obj = Faker(locale='zh_CN')
        self.faker_obj.add_provider(CarPlateProvider)

    def get_obj(self):
        """
        获取obj
        :return:
        """
        return self.faker_obj

    def get_list(self, cnt, par_list=None):
        """
        获取数据集
        :param cnt:
        :param par_list: name/name_male/name_female,ssn,address,company,phone_number等
        :return:
        """
        ret = []
        if not par_list:
            return ret
        for i in range(cnt):
            j_obj = {}
            for c in par_list:
                if c == "time_":
                    c_nr = self.faker_obj.time(pattern="%H:%M:%S")
                else:
                    c_nr = eval(f"self.faker_obj.{c}()")
                j_obj[c] = c_nr
            ret.append(j_obj)
        return ret

    @staticmethod
    def data_key(k=None):
        """
        数据字典说明
        :param k: 模糊搜索
        :return:
        """
        ret = [{"name": "姓名"}, {"name_male": "男性姓名"}, {"name_female": "女性姓名"},
               {"ssn": "身份证"}, {"address": "地址住址"}, {"company": "公司名企业名"},
               {"phone_number": "手机号码电话号码"}, {"ascii_safe_email": "示例邮箱email"}, {"ascii_free_email": "随机邮箱email"},
               {"domain_name": "域名"}, {"ipv4": "随机ip地址ip4"}, {"ipv6": "随机ip地址ip6"},
               {"mac_address": "随机mac地址"}, {"uri": "随机uri网址"}, {"url": "随机url网址"},
               {"chrome": "随机chrome浏览器的user_anent信息"}, {"firefox": "随机firefox火狐浏览器的user_anent信息"},
               {"internet_explorer": "随机ie浏览器的user_anent信息"}, {"opera": "随机opera浏览器的user_anent信息"},
               {"safari": "随机safari浏览器的user_anent信息"}, {"user_agent": "随机浏览器的user_anent信息"},
               {"sentence": "随机一句话(无意义)"}, {"paragraph": "随机一个段落一段话(无意义)"}, {"text": "随机一篇文章(无意义)"},
               {"word": "随机一个词语"}, {"md5": "随机32位小写md5"}, {"password": "随机密码"},
               {"sha1": "随机sha1"}, {"sha256": "随机sha256"}, {"date": "随机日期"},
               {"profile": "随机人员信息人员档案"}, {"simple_profile": "随机简要人员信息人员档案"},
               {"hex_color": "随机16进制颜色"}, {"rgb_color": "随机rgb颜色"},
               {"postcode": "邮编邮政编码"}, {"street_name": "道路名称街道名"}, {"time_": "随机时间"},
               {"car_no": "随机车号车牌号"},
               ]
        if not k:
            return ret
        ret_ = []
        for d in ret:
            for v in d.values():
                if k in v:
                    ret_.append(d)
                    break
        return ret_


if __name__ == "__main__":
    pass

from django.db import models


# Create your models here.

class DrVisitorInfo(models.Model):
    """
    访问者信息
    """

    VISITOR_TYPE = (
        ('read', '阅读'),
    )

    id = models.CharField(verbose_name='id', max_length=40, primary_key=True, db_column='id')
    add_time = models.DateTimeField(verbose_name="添加时间", blank=True, null=True)
    app_name = models.CharField(verbose_name='子系统模块名', max_length=40, blank=True)
    visitor_type = models.CharField(verbose_name='访客类型', choices=VISITOR_TYPE, max_length=10, blank=True)
    link_id = models.CharField(verbose_name='关联id', max_length=40, blank=True)
    visitor_ip = models.CharField(verbose_name="访问者ip", max_length=20, blank=True)
    visitor_lat = models.CharField(verbose_name="访问者纬度", max_length=30, blank=True)
    visitor_lng = models.CharField(verbose_name="访问者经度", max_length=30, blank=True)
    visitor_city = models.CharField(verbose_name="访问者城市", max_length=30, blank=True)
    visitor_addr = models.TextField(verbose_name="访问者位置描述", blank=True, null=True)
    cnt_ipstack = models.IntegerField(verbose_name="解析次数_ipstack", default=0)

    class Meta:
        db_table = "dr_visitor_info"


SQL_DIC_VISITOR = {
    "table1": DrVisitorInfo._meta.db_table,
    "table1_id": DrVisitorInfo.id.field_name,
    "table1_atime": DrVisitorInfo.add_time.field_name,
    "table1_appname": DrVisitorInfo.app_name.field_name,
    "table1_vtype": DrVisitorInfo.visitor_type.field_name,
    "table1_linkid": DrVisitorInfo.link_id.field_name,
    "table1_ip": DrVisitorInfo.visitor_ip.field_name,
    "table1_lat": DrVisitorInfo.visitor_lat.field_name,
    "table1_lng": DrVisitorInfo.visitor_lng.field_name,
    "table1_city": DrVisitorInfo.visitor_city.field_name,
    "table1_addr": DrVisitorInfo.visitor_addr.field_name,
    "table1_ipstack": DrVisitorInfo.cnt_ipstack.field_name,
}

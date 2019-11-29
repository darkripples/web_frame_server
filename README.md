# Web-Frame-Server
django2的一个web应用,数据库使用postgresql

## 依赖
```python
pip37 install django
pip37 install django-cors-headers
pip37 install uwsgi
pip37 install psycopg2
```
## 添加应用1-blog 

当前项目有个blog应用
> 1.只有blog的查看相关api 
>
> 2.blog的存储采用markdown格式
```python
python37 manage.py makemigrations
python37 manage.py migrate
```
> 3.需修改conf下的配置文件，通过__init__文件指定
## Log
 * 2019-02-02  
 > 初始化应用  
 * 2019-11-15   
 > 添加blog应用  
  * 2019-11-29   
 > 规范性改造  
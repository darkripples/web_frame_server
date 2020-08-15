# Web-Frame-Server
django2的一个web应用,数据库使用postgresql

## 依赖
```python
pip3 install django
pip3 install django-cors-headers
pip3 install uwsgi
pip3 install psycopg2
```
## 添加应用-blog 

当前项目有个blog应用(dr应用为底层共同模块)
> 1.只有blog的查看相关api 
>
> 2.blog的存储采用markdown格式
```python
python3 manage.py makemigrations
python3 manage.py migrate
```
> 3.需修改conf下的配置文件，通过__init__文件指定  
> 4.db初始化
```sql
-- 初始化.密码为123456
insert into dr_roles(id, role_name, add_time, level, order_no, visible)
    values('sa', '超管', now(), '1', 99, '0');
INSERT INTO dr_user("id", "account", "user_name", "pwd_value", "pwd_salt", "phone", "email", "wx_link_id", "qq_link_id", "add_time", "upd_time", "email_succ") 
    VALUES ('1', 'super_admin', '超级管理员', '44CA28DAC965885B03FDD1C0013A5E44', 'PNRtaS5i', '13111111111', '', NULL, NULL, now(), now(), NULL);
insert into dr_user_info(id,sex_type,add_time, upd_time)
    values('1', '9', now(), now());
insert into dr_user_roles(id, user_id, role_id)
    values('1', '1', 'sa');
insert into dr_menu(id, pid, show_name, alias_name, href, icon, order_no, add_time)
    values('99', null, '系统管理', '系统管理[超级管理员]', '', 'ant ant-setting', 99, now());
insert into dr_menu(id, pid, show_name, alias_name, href, icon, order_no, add_time)
    values('9901', '99', '用户管理', '用户管理[超级管理员]', '/dr/manage/sys/user/list.html', '', 9901, now());
insert into dr_menu(id, pid, show_name, alias_name, href, icon, order_no, add_time)
    values('9902', '99', '角色管理', '角色管理[超级管理员]', '/dr/manage/sys/role/list.html', '', 9902, now());
insert into dr_menu(id, pid, show_name, alias_name, href, icon, order_no, add_time)
    values('9903', '99', '菜单管理', '菜单管理[超级管理员]', '/dr/manage/sys/menu/list.html', '', 9903, now());
insert into dr_role_menu(id, role_id, menu_id, add_time)
    values('1', 'sa', '99', now());
insert into dr_role_menu(id, role_id, menu_id, add_time)
    values('11', 'sa', '9901', now());
insert into dr_role_menu(id, role_id, menu_id, add_time)
    values('12', 'sa', '9902', now());
insert into dr_role_menu(id, role_id, menu_id, add_time)
    values('13', 'sa', '9903', now());

INSERT INTO dr_menu("id", "pid", "show_name", "alias_name", "href", "icon", "order_no", "upd_user_id", "add_time") 
    VALUES ('blog', null, '博客管理', '博客管理', '', '', '1', '1', '2020-08-15 08:27:36.25853+08');
INSERT INTO dr_menu("id", "pid", "show_name", "alias_name", "href", "icon", "order_no", "upd_user_id", "add_time") 
    VALUES ('blog1', 'blog', '文章管理', '文章管理[博客管理]', '/blog/manage/content/list.html', '', '1', '1', '2020-08-15 08:31:31.854217+08');
insert into dr_role_menu(id, role_id, menu_id, add_time)
    values('b', 'sa', 'blog', now());
insert into dr_role_menu(id, role_id, menu_id, add_time)
    values('b11', 'sa', 'blog1', now());

```
> 5.nginx里，需增加静态文件配置  
```nginx
location /static {
    # 同之前设置的uwsgi的路径一直，固定应用名称为app_dr,因为在该应用中配置的static静态路由
    rewrite ^/(.*)$ http://127.0.0.1:9797/app_dr/$1 permanent;
    access_log   off;
}
```
完整nginx可参考如下(后端应用端口假设为9797):
```nginx
server {
        listen       8000;
        server_name  127.0.0.1;
        location /app_dr/ {
            proxy_pass http://127.0.0.1:9797/;
        }
        location /app_blog/ {
            proxy_pass http://127.0.0.1:9797/;
        }
        location /img/ {
            root E:/Projects/pythonWorkspace/moreAppTest/web_frame_front/common/static/;
        }
        location /common/ {
            # common-disk-resources.页面静态资源调用
            alias E:/Projects/pythonWorkspace/moreAppTest/web_frame_front/common/;
            access_log   off;
        }
        location /dr {
            # dr-index.URL入口
            alias E:/Projects/pythonWorkspace/moreAppTest/web_frame_front/dr/pages/;
            access_log   off;
        }
        location /dr_resources {
            # dr-disk-resources.页面静态资源调用
            alias E:/Projects/pythonWorkspace/moreAppTest/web_frame_front/dr/;
            access_log   off;
        }
        
        location /blog {
            # blog-index.URL入口
            alias E:/Projects/pythonWorkspace/moreAppTest/web_frame_front/blog/pages/;
            access_log   off;
        }
        location /blog_resources {
            # blog-disk-resources.页面静态资源调用
            alias E:/Projects/pythonWorkspace/moreAppTest/web_frame_front/blog/;
            access_log   off;
        }
        location /static {
            rewrite ^/(.*)$ http://127.0.0.1:9797/app_dr/$1 permanent;
            access_log   off;
        }
    }
```
> 6.后端地址为：
http://127.0.0.1:8000/dr/manage/index.html
用户名：super_admin
密码： 123456

## todo
后台新增时，还未关联到markdown实时预览  
## Log
 * 2019-02-02  
 > 初始化应用  
 * 2019-11-15   
 > 添加blog应用  
  * 2019-11-29   
 > 规范性改造  
  * 2020-08-15
 > 增加后台管理模块、规范前后端,升级utils版本

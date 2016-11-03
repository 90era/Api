# Team.API
Api for Team Blog System

# LICENSE
MIT

# 使用
> 1. yum -y install mysql-devel python-devel python-pip gcc gcc-c++
> 2. pip install -r requirements.txt
> 3. 修改pub/config.py配置文件，四段内容，GLOBAL、PRODUCT、MYSQL、BLOG，根据实际情况配置。
> 4. sh ./ControlTeamApiRun.sh
> 5. 部署到Web服务器(Nginx)
```
server {
    listen 443;
    server_name YourDomainName;
    if ($host != "YourDomainName") {
      rewrite ^/(.*)$ http://www.saintic.com/$1 permanent;
    }
    charset utf-8;
    ssl     on;
    ssl_certificate      certs/your.crt;
    ssl_certificate_key  certs/your.key;
    location / {
       proxy_pass http://127.0.0.1:10040; #设置为实际IP+PORT
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-Proto https;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       #add_header  Content-Type 'application/json; charset=utf-8';
       #add_header X-Cache $upstream_cache_status;
    }
}
server {
    listen 80;
    server_name YourDomainName;
    #rewrite ^/(.*)$ http://www.saintic.com/$1 permanent;
    #这里去掉rewrite注释跳转到https，但是发现这样单元测试请求http时发生请求异常，所以注释，非测试下建议去掉注释，强制跳转到https！
    charset utf-8;
    location / {
       proxy_pass http://127.0.0.1:10040;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-Proto https;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

此时```netstat -anptl | grep Team.Api```查看进程，应该可以看到类似以下的信息(其中Team.Api是你配置文件中定义的)：

```tcp        0      0 0.0.0.0:10040               0.0.0.0:*                   LISTEN      31355/Team.Api```

或者```ps aux | grep Team.Api```过滤下，应该可以看到类似以下的信息(其中Team.Api是你配置文件中定义的)：

```500      31355  0.0  2.1 334368 21424 ?        S    May20   0:00 Team.Api```

如果没有正常监听系统，请直接运行，查看具体输出或查看logs/sys.log：

```python src/Product.py```

如有问题，请到[https://github.com/saintic/Team/issues][1]提出问题。

[1]: https://github.com/saintic/Team/issues

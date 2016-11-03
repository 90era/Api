# -*- coding:utf8 -*-

#全局配置端
GLOBAL={

    "Host": "0.0.0.0",
    #Application run network address, you can set it `0.0.0.0`, `127.0.0.1`, ``, `None`;
    #Default run on all network interfaces.

    "Port": 10040,
    #Application run port, default port;

    "Debug": True,
    #The development environment is open, the production environment is closed, which is also the default configuration.

    "LogLevel": "DEBUG",
    #应用程序写日志级别，目前有DEBUG，INFO，WARNING，ERROR，CRITICAL

    "put2Redis": False
    #将应用注册到信息中心。

}

#生产环境配置段
PRODUCT={

    "ProcessName": "Api",
    #Custom process, you can see it with "ps aux|grep ProcessName".

    "ProductType": "tornado",
    #生产环境启动方法，可选`gevent`, `tornado`, `uwsgi`,其中tornado log level是WARNNING，也就是低于WARN级别的日志不会打印或写入日志中。
}

#数据库配置段
MYSQL={
    "Host": "127.0.0.1",
    "Port": 3306,
    "Database": "team",
    "User": "root",
    "Passwd": "123456",
    "Charset": "utf8",
    "Timezone": "+8:00",
    #MySQL连接信息，格式可包括在()、[]、{}内，分别填写主机名或IP、端口、数据库、用户、密码、字符集、时区等，其中port默认3306、字符集默认utf8、时区默认东八区，注意必须写在一行内！
}


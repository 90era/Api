# -*- coding:utf8 -*-

import re
import time
import torndb
import hashlib
import datetime
import requests
import commands
import binascii, os, uuid
from log import Syslog
from db import DB
from config import GLOBAL, MYSQL, PRODUCT


md5           = lambda pwd:hashlib.md5(pwd).hexdigest()
mysql         = DB()
logger        = Syslog.getLogger()
gen_token     = lambda :binascii.b2a_base64(os.urandom(24))[:32]
gen_requestId = lambda :str(uuid.uuid4())

#API所需要的正则表达式
mail_check    = re.compile(r'([0-9a-zA-Z\_*\.*\-*]+)@([a-zA-Z0-9\-*\_*\.*]+)\.([a-zA-Z]+$)')
chinese_check = re.compile(u"[\u4e00-\u9fa5]+")
ip_pat        = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")

#获取今天的日期
today = lambda :datetime.datetime.now().strftime("%Y-%m-%d")

#用户上传文件随机命名
gen_rnd_filename = lambda :"%s%s" %(datetime.datetime.now().strftime('%Y%m%d%H%M%S'), str(random.randrange(1000, 10000)))

mysql2 = lambda :torndb.Connection(
                    host     = "%s:%s" %(MYSQL.get('Host'), MYSQL.get('Port', 3306)),
                    database = MYSQL.get('Database'),
                    user     = MYSQL.get('User', None),
                    password = MYSQL.get('Passwd', None),
                    time_zone= MYSQL.get('Timezone','+8:00'),
                    charset  = MYSQL.get('Charset', 'utf8'),
                    connect_timeout=3,
                    max_idle_time=5
        )

def ip_check(ip):
    logger.info("the function ip_check param is %s" %ip)
    if isinstance(ip, (str, unicode)):
        return ip_pat.match(ip)

#API所需要的公共函数
def dbUser(username=None, password=False, token=False, uid=False):
    """
    1. 获取数据库中所有用户或是否存在某个具体用户(方法: username=username)。
    2. 当username为真，password=True, 获取用户及密码。
    3. 当username为真，token=True，获取用户及token。
    4. 当username为真，password、token皆为True，获取用户、密码、token。
    5. 当username不存在，即第一条解释。
    """
    if username:
        if password == True:
            if token == True:
                if uid == True:
                    sql = "SELECT ic,username,password,token FROM user WHERE username='%s'" % username
                else:
                    sql = "SELECT username,password,token FROM user WHERE username='%s'" % username
            else:
                if uid == True:
                    sql = "SELECT id,username,password FROM user WHERE username='%s'" % username
                else:
                    sql = "SELECT username,password FROM user WHERE username='%s'" % username
        else:
            if token == True:
                if uid == True:
                    sql = "SELECT id,username,token FROM user WHERE username='%s'" % username
                else:
                    sql = "SELECT username,token FROM user WHERE username='%s'" % username
            else:
                if uid == True:
                    sql = "SELECT id,username FROM user WHERE username='%s'" % username
                else:
                    sql = "SELECT username FROM user WHERE username='%s'" % username
    else:#All user from mysql(team.user)
        sql = "SELECT username FROM user"
    logger.info({"func:dbUser:sql":sql})
    try:
        data = mysql.get(sql)
    except Exception, e:
        logger.warn(e)
        return None
    else:
        return data

def postData(request, res):
    logger.debug(request.headers)
    logger.debug(request.json)
    logger.debug(request.form)
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        email    = request.json.get('email', None)
    except Exception,e:
        logger.warn("No request.json, start request.form, get exceptions %s"%e)
        try:
            username = request.form.get('username', None)
            password = request.form.get('password', None)
            email    = request.form.get('email', None)
        except Exception, e:
            logger.error(e)
            res['msg'] = 'No username or password in request, you maybe set headers with "Content-Type: application/json" next time.'
            res['code']= code + 1
    return {"data":(username, password, email), "res": res}

# 计算加密cookie:
def make_signed_cookie(uid, password, max_age):
    expires = str(int(time.time() + max_age))
    L = [uid, expires, hashlib.md5('%s-%s-%s-%s' % (uid, password, expires, _COOKIE_KEY)).hexdigest()]
    return '-'.join(L)

# 解密cookie:
def parse_signed_cookie(cookie_str):
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        id, expires, md5 = L
        if int(expires) < time.time():
            return None
        user = User.get(id)
        if user is None:
            return None
        if md5 != hashlib.md5('%s-%s-%s-%s' % (id, user.password, expires, _COOKIE_KEY)).hexdigest():
            return None
        return user
    except:
        return None

def get_ip(getLanIp=False):
    _WanIpCmd = "/sbin/ifconfig | grep -o '\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}' | grep -vE '192.168.|172.1[0-9]|172.2[0-9]|172.3[0-1]|10.[0-254]|255|127.0.0.1|0.0.0.0'"
    _WanIp    = commands.getoutput(_WanIpCmd).replace("\n", ",")
    if _WanIp:
        logger.info("First get ip success, WanIp is %s with cmd(%s), enter LanIp." %(_WanIp, _WanIpCmd))
    else:
        _WanIp = requests.get("http://members.3322.org/dyndns/getip", timeout=3).text.strip()
        if ip_check(_WanIp):
            logger.info("Second get ip success, WanIp is %s with requests, enter LanIp." %_WanIp)
        else:
            logger.error("get_ip fail")
            return ('', '')
    if getLanIp == True:
        _LanIpCmd = "/sbin/ifconfig | grep -o '\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}' | grep -vE '255|0.0.0.0|127.0.0.1' | sort -n -k 3 -t . | grep -E '192.168.|172.1[0-9]|172.2[0-9]|172.3[0-1]|10.[0-9]'"
        _LanIp    = commands.getoutput(_LanIpCmd).replace("\n", ",") or 'Unknown'
        logger.info("Get ip success, LanIp is %s with cmd(%s), over IP." %(_LanIp, _LanIpCmd))
        Ips = (_WanIp, _LanIp)
    else:
        Ips = (_WanIp,)
    return Ips

def put2Redis():
    def Ips():
        _WanIps, _LanIps = get_ip(getLanIp=True)
        logger.debug("wanip(%s), lanip(%s)" %(_WanIps, _LanIps))
        WanIp = _WanIps if len(_WanIps.split(",")) == 1 else _WanIps.split(",")[0]
        LanIp = _LanIps if len(_LanIps.split(",")) == 1 else _LanIps.split(",")[0]
        return WanIp, LanIp, _WanIps, _LanIps
    WanIp, LanIp, _WanIps, _LanIps = Ips()
    Host = GLOBAL.get('Host')
    Port = GLOBAL.get('Port')
    LogLevel    = GLOBAL.get('LogLevel')
    ProcessName = PRODUCT.get('ProcessName')
    ProductType = PRODUCT.get('ProductType')
    while True:
        if ip_check(WanIp):
            logger.info("You will register something information into redis.")
            data = {"application_name": ProcessName, "application_port": Port, "application_loglevel": LogLevel, "application_wanip": WanIp, "application_lanip": _LanIps, "application_protype": ProductType}
            req  = requests.post("https://passport.saintic.com/registry/", data=data, verify=False, timeout=5)
            try:
                res = req.json() 
                if res == True:
                    logger.info("Register redis success!")
                else:
                    logger.error("Register redis fail!!!")
            except Exception,e:
                logger.error(e)
        else:
            logger.warn("ip invaild, continue.")
            WanIp, LanIp, _WanIps, _LanIps = Ips()
            continue
        time.sleep(10)

if __name__ == "__main__":
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    _cn = "Mr.tao先生"
    _cn = unicode(_cn)
    res = chinese_check.search(_cn)
    if res:
        print "has Chinese"
    else:
        print 'no Chinese'

# -*- coding:utf-8 -*-

from pub import logger, config, mysql
from flask import request
from flask.ext.restful import Resource

class Conf(Resource):
    """/conf资源, get/post, post详细参数,但必须添加token头和username参数。"""

    def get(self):
        res = {"url": request.url, "msg": "ConfigControlCenter(C3)", "code": 0}
        res["C3"] = config.C3
        logger.info(res)
        return res

    def post(self):
        res = {"url": request.url, "msg": "ConfigControlCenter(C3)", "code": 0}
        #get mysql config
        _ReqToken = request.headers.get("token", None)
        _ReqUser  = request.args.get("username", None)
        _ReqMysql = request.args.get("mysql", False)
        sql = "SELECT username,token FROM user WHERE username='%s' AND token='%s' LIMIT 1" %(_ReqUser, _ReqToken)
        if _ReqMysql == "true" or _ReqMysql == True:
            try:
                if mysql.get(sql):
                    res["C3"]   = config.C3
                    res["C3"]["MYSQL"] = config.MYSQL
                    res["msg"]  = "C3: username match token successful"
                else:
                    res["msg"]  = "C3: username match token failed"
                    res["code"] = 1040
            except Exception,e:
                logger.error(e)
                res.update({"msg": "exception", "code": 1041})
        logger.info({"res": res, "Conf:post:SQL": sql})
        return res

# -*- coding:utf-8 -*-

from pub import logger, mysql, dbUser, md5, gen_token, postData
from flask import request, g
from flask.ext.restful import Resource

class Token(Resource):
    def post(self):
        """create token, with post data:
        1. username,
        2. password,
        return token
        """
        code= 1030
        res = {"url": request.url, "msg": None, 'code': code}
        _Pd = postData(request, res)
        logger.debug({"Token:tool:postData": _Pd})
        try:
            username, password, email, res = _Pd.get("data")[0], _Pd.get("data")[1],  _Pd.get("data")[2], _Pd.get("res")
        except (AttributeError, IndexError), e:
            res.update({'msg': "Server Error", "code": 500})
            logger.error(res)
            logger.error(e)
            return res
        #login check(as a function), in user.py(User:post:action=log)
        ReqData = dbUser(username, password=True, token=True)
        if not ReqData:
            res['msg'] = 'User not exists'
            res['code']= code + 2
            logger.warn(res)
            return res
        #ReqData is True(user is exists), it's dict, eg:{'username': u'xxxxx', 'password': u'xxxxxxxxxx'}
        _Reqpass = md5(password)
        _DBuser  = ReqData.get('username')
        _DBpass  = ReqData.get('password')
        _DBtoken = ReqData.get('token')
        if _DBtoken:
            res.update({'msg': 'Token already exists', 'code': code + 3, "token": _DBtoken})
            logger.warn(res)
            return res
        if _Reqpass == _DBpass:
            token = gen_token()
            res.update({'msg': 'username + password authentication success, token has been created.', 'code': 0, 'token': token})
            sql = "UPDATE user SET token='%s' WHERE username='%s'" % (token, username)
            try:
                mysql.update(sql)
                logger.info('Token:post:create_token:sql--> "%s"' %sql)
            except Exception,e:
                logger.error(e)
                res['msg'] = 'token insert error' #had token for return
                return res
        else:
            res.update({'msg': 'username + password authentication failed', 'code': code + 4})
        logger.info(res)
        return res

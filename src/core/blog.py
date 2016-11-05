# -*- coding:utf-8 -*-

from pub import logger, mysql, mysql2, today
from flask import request
from flask.ext.restful import Resource

class Blog(Resource):

    def get(self):
        """/blog资源，参数是
        1.num|limit(int, str), 限制列出数据数量，另外可设置为all，列出所有blog， 全局参数。
        2.sort(str), 数据排序, 全局参数。
        3.blogId(int), 查询某一个id的文章, 独立参数。
        4.get_catalog_list(bool), 列出博客所有目录，独立参数。
        5.get_sources_list(bool), 列出博客所有类型，独立参数。
        6.get_catalog_data(str), 查询博客某目录下的num个文章。
        7.get_sources_data(str), 查询博客某类型下的num个文章。
        8.get_index_only(bool),仅仅查询所有博客标题、ID、创建时间。
        9.get_user_blog(str),查询某用户的所有博客。
        """
        num    = request.args.get('num', request.args.get('limit', 10))
        LIMIT  = '' if num in ("all", "All") else "LIMIT " + str(num)
        sort   = request.args.get('sort', 'desc')
        blogId = request.args.get('blogId')
        get_catalog_list = True if request.args.get("get_catalog_list") in ("true", "True", True) else False
        get_sources_list = True if request.args.get("get_sources_list") in ("true", "True", True) else False
        get_catalog_data = request.args.get("get_catalog_data")
        get_sources_data = request.args.get("get_sources_data")
        get_index_only   = True if request.args.get("get_index_only") in ("true", "True", True) else False
        get_user_blog    = request.args.get("get_user_blog")

        res    = {"url": request.url, "msg": None, "data": None, "code": 0}
        logger.debug({"num": num, "blogId": blogId, "get_catalog_list": get_catalog_list, "get_sources_list": get_sources_list, "get_catalog_data": get_catalog_data, "get_sources_data": get_sources_data})

        if get_sources_data:
            if get_sources_data.lower()[:3] == "ori":
                get_sources_data = '原创'
            elif get_sources_data.lower()[:3] == "rep":
                get_sources_data = '转载'
            elif get_sources_data.lower()[:3] == "tra":
                get_sources_data = '翻译'
            #Original reproduced translation

        if get_index_only:
            sql = "SELECT id,title,create_time,update_time FROM team.blog ORDER BY id %s %s" %(sort, LIMIT)
            logger.info("SELECT title only SQL: %s" %sql)
            try:
                data = mysql2().query(sql)
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(data=[], msg="Only title query fail", code=7)
            else:
                res.update(data=data)
            logger.info(res)
            return res
        
        if get_catalog_list and get_sources_list:
            sql="SELECT sources,catalog FROM team.blog"
            logger.info("get_catalog_sources_list SQL: %s" %sql)
            data=mysql2().query(sql)
            sources=set()
            catalog=set()
            for i in data:
                sources.add(i.get("sources"))
                catalog.add(i.get("catalog"))
            res.update(data={"sources": sorted(list(sources)), "catalog": sorted(list(catalog))})
            logger.info(res)
            return res

        if get_catalog_list:
            sql = "SELECT GROUP_CONCAT(catalog) FROM blog GROUP BY catalog"
            logger.info("SELECT catalog list SQL: %s" %sql)
            try:
                data = mysql.get(sql)
                logger.info(data)
                data = [ v.split(",")[0] for i in data for v in i.values() if v and v.split(",")[0] ]
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(data=[], msg="Catalog query fail", code=1)
            else:
                res.update(data=data)
            logger.info(res)
            return res

        if get_sources_list:
            sql = "SELECT GROUP_CONCAT(sources) FROM blog GROUP BY sources"
            logger.info("SELECT sources list SQL: %s" %sql)
            try:
                data = mysql.get(sql)
                logger.info(data)
                data = [ v.split(",")[0] for i in data for v in i.values() if v and v.split(",")[0] ]
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(data=[], msg="Sources query fail", code=2)
            else:
                res.update(data=data)
            logger.info(res)
            return res

        if get_catalog_data:
            sql = "SELECT id,title,content,create_time,update_time,tag,catalog,sources,author FROM team.blog WHERE catalog='%s' ORDER BY id %s %s" %(get_catalog_data, sort, LIMIT)
            logger.info("SELECT catalog data SQL: %s" %sql)
            try:
                data = mysql2().query(sql)
                logger.info(data)
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(data=[], msg="Catalog data query fail", code=3)
            else:
                res.update(data=data)
            logger.info(res)
            return res

        if get_sources_data:
            sql = "SELECT id,title,content,create_time,update_time,tag,catalog,sources,author FROM team.blog WHERE sources='%s' ORDER BY id %s %s" %(get_sources_data, sort, LIMIT)
            logger.info("SELECT sources data SQL: %s" %sql)
            try:
                data = mysql2().query(sql)
                logger.info(data)
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(data=[], msg="Sources data query fail", code=4)
            else:
                res.update(data=data)
            logger.info(res)
            return res

        if get_user_blog:
            sql = "SELECT id,title,create_time,tag,catalog,sources,author from team.blog WHERE author='%s' ORDER BY id %s %s" %(get_user_blog, sort, LIMIT)
            logger.info("SELECT user blog SQL: %s" %sql)
            try:
                data = mysql2().query(sql)
            except Exception,e:
                logger.error(e, exc_info=True)
                res.update(data=[], msg="User blog data query fail", code=7)
            else:
                res.update(data=data)
            logger.info(res)
            return res

        if blogId:
            sql = "SELECT id,title,content,create_time,update_time,tag,catalog,sources,author FROM team.blog WHERE id=%s" %blogId
        elif num:
            sql = "SELECT id,title,content,create_time,update_time,tag,catalog,sources,author FROM team.blog ORDER BY id %s %s" %(sort, LIMIT)
        else:
            res.update(msg="The query error", code=5)
            logger.info(res)
            return res
        logger.info({"Blog:get:SQL": sql})
        try:
            data = mysql.get(sql)
        except Exception,e:
            logger.error(e, exc_info=True)
            res.update(msg="get blog error", code=6)
        else:
            res.update(data=data)

        logger.info(res)
        return res

    def post(self):
        """ 创建博客文章接口 """
        #get blog form informations.
        blog_title   = request.form.get('title')
        blog_content = request.form.get('content')
        blog_ctime   = today()
        blog_tag     = request.form.get("tag")
        blog_catalog = request.form.get("catalog", "linux")
        blog_sources = request.form.get("sources", "原创")
        blog_author  = request.form.get("author")
        logger.info("blog_title:%s, blog_content:%s, blog_ctime:%s, blog_tag:%s, blog_catalog:%s, blog_sources:%s, blog_author:%s" %(blog_title, blog_content, blog_ctime, blog_tag, blog_catalog, blog_sources, blog_author))
        if blog_title and blog_content and blog_ctime and blog_author:
            #sql = 'INSERT INTO blog (title,content,create_time,tag,catalog,sources) VALUES ("%s", "%s", "%s", "%s", "%s", "%s")'
            sql = 'INSERT INTO blog (title,content,create_time,tag,catalog,sources,author) VALUES (%s, %s, %s, %s, %s, %s, %s)'
            logger.info(sql %(blog_title, blog_content, blog_ctime, blog_tag, blog_catalog, blog_sources, blog_author))
            try:
                blog_id  = mysql2().insert(sql, blog_title, blog_content, blog_ctime, blog_tag, blog_catalog, blog_sources, blog_author)
            except Exception,e:
                logger.error(e, exc_info=True)
                res = {"code": 3, "data": None, "msg": "blog write error."}
            else:
                res = {"code": 0, "data": blog_id, "msg": "blog write success."}
        else:
            res = {"code": 4, "data": None, "msg": "data form error."}
        logger.info(res)
        return res

    def put(self):
        """ 更新博客文章接口 """
        blog_title   = request.form.get('title')
        blog_content = request.form.get('content')
        blog_utime   = today()
        blog_tag     = request.form.get("tag")
        blog_catalog = request.form.get("catalog", "linux")
        blog_sources = request.form.get("sources", "原创")
        blog_author  = request.form.get("author")
        blog_blogId  = request.form.get("blogId")
        logger.info("Update blog, blog_title:%s, blog_content:%s, blog_utime:%s, blog_tag:%s, blog_catalog:%s, blog_sources:%s, blog_author:%s, blog_blogId:%s" %(blog_title, blog_content, blog_utime, blog_tag, blog_catalog, blog_sources, blog_author, blog_blogId))
        try:
            blog_blogId = int(blog_blogId)
        except ValueError,e:
            logger.error(e, exc_info=True)
            res = {"code": 5, "msg": "blog form error."}
        else:
            if blog_title and blog_content and blog_utime and blog_author:
                sql = "UPDATE blog SET title=%s,content=%s,update_time=%s,tag=%s,catalog=%s,sources=%s,author=%s WHERE id=%s"
                try:
                    mysql2().update(sql, blog_title, blog_content, blog_utime, blog_tag, blog_catalog, blog_sources, blog_author, blog_blogId)
                except Exception,e:
                    logger.error(e, exc_info=True)
                    res = {"code": 6, "msg": "blog write error."}
                else:
                    res = {"code": 0, "success": True, "msg": None}
            else:
                res = {"code": 7, "success": False, "msg": "blog form error."}
        logger.info(res)
        return res


FROM registry.saintic.com/alpine-python:gcc
MAINTAINER Mr.tao <staugur@saintic.com>
ADD ./src /Team.Api
WORKDIR /Team.Api
RUN apk add --no-cache mysql-client mysql-dev
RUN pip install Flask Flask-RESTful tornado gevent setproctitle MySQL-python torndb && chmod +x Product.py
EXPOSE 10040
ENTRYPOINT ["/Team.Api/Product.py"]

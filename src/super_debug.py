if __name__ == '__main__':
    from werkzeug.contrib.profiler import ProfilerMiddleware
    from pub.config import GLOBAL
    Host = GLOBAL.get('Host')
    Port = GLOBAL.get('Port')
    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [30])
    app.run(debug=True, host=Host, port=int(Port))

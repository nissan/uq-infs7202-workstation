def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    resp = "<h1 style='color:blue'>Welcome to My Python App!</h1>"
    return [resp.encode('utf-8')]

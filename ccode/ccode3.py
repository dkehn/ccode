#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import socket
import ssl
# import select
# import httplib
import urlparse
import threading
# import gzip
# import zlib
# import time
# import json
import random
# import re
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
# from cStringIO import StringIO
# from subprocess import Popen, PIPE
# from HTMLParser import HTMLParser


def with_color(c, s):
    return "\x1b[%dm%s\x1b[0m" % (c, s)


def join_with_script_dir(path):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

# class dbRouterEle():
#     def __init__(self, name, cstring, status, ):
#         self.cache_ele["name"] = {
#             "name", name,
#             "connection_string": ctring,
#             "status": status,
#             "data_filter": dfilter
#             "lru_cache": None
#             }

#         # At this point we would connect to the sonnection string,
#         # and set status = True, if successful

#     def name(self):
#         return self.cache_ele["name"]

#     def conn_string(self):
#         return self.cache_ele["connection_string"]

#     def status(self):
#         return self.cache_ele["status"]

#     def data_filter(self):
#         return self.cache_ele["data_filter"]


class DBRouter():
    CACHE_SIZE = (1024 * 64)
    '''This class is to handle databasdr routing, i.e. based upon a key
    which database will we pass the request to? Her are the assumptions:
    1) we have an understand of how the database url are organized
    2) there is something that can be used to route the DB requests like hostname or DNS

    If this a you design the db then for infinate scalabilty then that data will have to be shared.
    And assuming that level of control of the data then if not shard key is avialable paralellizing
    the malware lookup is required.

    The router_cache will defined as follows:
    router_cache {
       name
       connection_string
       status  (True connection/ Flase not connected)
       data_filter  ( the lookup against the hostname or Ipaddr to define if the host name is here,
                 assuming that the filter must be applied and not a dict type lookup )
       lookup_cache (LRU cache to lookup against this db, see CACHE_SIZE for sizing info)
       cache_size ( Current elements in the cache )
    '''
    def __init__(self):
        self.router_cache = {}

    # def add(self, name, cstring, status, dfilter):
    #     if not self.router[name]:
    #         self.router['name'] = dbRouterEle(name, cstring, status, dfilter)
    #         self.
    #         self.router[name] = {"name": name, connection_string: cstring, }
    #         c_ele = self.router[name]

    #         c_ele = {


class urlLookup():
    def __init__(self):
        pass

    def check(self, host, port=80, path_and_query=None):
        return random.randint(0, 1)


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    address_family = socket.AF_INET6
    daemon_threads = True

    def handle_error(self, request, client_address):
        # surpress socket/ssl related errors
        cls, e = sys.exc_info()[:2]
        if cls is socket.error or cls is ssl.SSLError:
            pass
        else:
            return HTTPServer.handle_error(self, request, client_address)


class RequestHandler(BaseHTTPRequestHandler):
    cakey = join_with_script_dir('ca.key')
    cacert = join_with_script_dir('ca.crt')
    certkey = join_with_script_dir('cert.key')
    certdir = join_with_script_dir('certs/')
    timeout = 5
    lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        self.tls = threading.local()
        self.tls.conns = {}

        self.url_validation = urlLookup()

        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def log_error(self, format, *args):
        # surpress "Request timed out: timeout('timed out',)"
        if isinstance(args[0], socket.timeout):
            return

        self.log_message(format, *args)

    def do_GET(self):
        if self.path == 'http://proxy2.test/':
            self.send_cacert()
            return

        req = self
        content_length = int(req.headers.get('Content-Length', 0))
        req_body = self.rfile.read(content_length) if content_length else None

        if req.path[0] == '/':
            if isinstance(self.connection, ssl.SSLSocket):
                req.path = "https://%s%s" % (req.headers['Host'], req.path)
            else:
                req.path = "http://%s%s" % (req.headers['Host'], req.path)

        req_body_modified = self.request_handler(req, req_body)
        if req_body_modified is False:
            self.send_error(403)
            return
        elif req_body_modified is not None:
            req_body = req_body_modified
            req.headers['Content-length'] = str(len(req_body))

        u = urlparse.urlsplit(req.path)
        host = u.path.split('/')[2]
        port = None
        if host.find(':') >= 0:
            port = host.split(':')[1]
            host = host.split(':')[0]
        hostip = socket.gethostbyname(host)

        scheme, netloc, path = u.scheme, u.netloc, (u.path + '?' + u.query if u.query else u.path)

        if port:
            path_and_query = path[path.find(port) + len(port) + 1:]
        else:
            path_and_query = path[path.find(host) + len(host) + 1:]

        assert scheme in ('http', 'https')
        if netloc:
            req.headers['Host'] = netloc
        setattr(req, 'headers', self.filter_headers(req.headers))

        # import pdb; pdb.set_trace()
        if hostip:
            if self.url_validation.check(host, port, path_and_query):
                res_body = ("This URL:%s is SAFE" % (host))
            else:
                res_body = ("This URL:%s is NOT SAFE" % (host))
        else:
            res_body = ("This URL:%s is NOT FOUND" % (host))

        resp_buf = ("<html><head><title>URL Lookup Service</title>"
                    "</head>\n<p>URL: %s  ip: %s\nResult: %s</p>" %
                    (host, hostip, res_body))
        resp_buf += "</body></html>\n\n"
        content_len = len(resp_buf)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", content_len)
        self.end_headers()
        self.wfile.write(resp_buf)

    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET
    do_OPTIONS = do_GET

    def request_handler(self, req, req_body):
        pass

    def response_handler(self, req, req_body, res, res_body):
        pass

    def save_handler(self, req, req_body, res, res_body):
        self.print_info(req, req_body, res, res_body)


def main(HandlerClass=RequestHandler, ServerClass=ThreadingHTTPServer, protocol="HTTP/1.1"):
    # import pdb; pdb.set_trace()
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8080
    # server_address = ('::1', port) # localhost only
    server_address = ('', port)

    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    this_host = socket.gethostname()
    print "HTTP Proxy Maliware Service on", this_host, "port", sa[1], "..."
    httpd.serve_forever()


if __name__ == '__main__':
    main()

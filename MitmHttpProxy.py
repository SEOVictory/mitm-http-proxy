import SocketServer
import SimpleHTTPServer

import logging as log

from threading import Thread
from time import sleep

from CollectAllProxy import CollectAllProxy


def shutdown_thread(t):
    log.info("shutting down thread")
    t.shutdown()
    while t.isAlive():
        sleep(.1)
    log.info("done shutting down thread")


class ReusableTCP(SocketServer.TCPServer):
    allow_reuse_address = True


class Httpd(Thread):
    httpd = None

    def __init__(self):
        super(Httpd, self).__init__()

        self.PORT = 8000
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        self.httpd = ReusableTCP(("", self.PORT), Handler)
        self.httpd.timeout = 3
        log.info("serving at port %s" % self.PORT)

    def run(self):
        self.httpd.serve_forever()

    def shutdown(self):
        log.debug("Shutting down httpd")
        self.httpd.shutdown()
        log.debug("Done with httpd shutdown")


class MitmHttpProxy(CollectAllProxy):
    inject_body_function = None
    inject_body_condition_function = None

    def inject_body(self, response):
        ijb = self.inject_body_function
        ijc = self.inject_body_condition_function

        if not hasattr(ijb, '__call__'):
            return response

        if hasattr(ijc, '__call__'):
            if not self.inject_body_condition_function(response):
                return response

        response.inject_body(ijb)
        return response

# -*- coding: utf-8 -*-
from dirg_util.http_util import Redirect
import importlib
import argparse
from cherrypy import wsgiserver


def application(environ, start_response):
    """
    WSGI application. Handles all requests.
    This application only performs a redirect to the HTTPS server for dirg_web.
    :param environ: WSGI enviroment.
    :param start_response: WSGI start response.
    :return: Depends on the request. Always a WSGI response where start_response first have to be initialized.
    """
    return Redirect(config.ISSUER)(environ, start_response)


if __name__ == '__main__':
    #This is equal to a main function in other languages. Handles all setup and starts the server.

    #Read arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="config")
    args = parser.parse_args()
    global config
    config = importlib.import_module(args.config)


    if config.HTTPS:
        global srv
        srv = wsgiserver.CherryPyWSGIServer(('0.0.0.0', config.HTTP_PORT), application)
        srv.stats['Enabled'] = True
        print "Redirect server is listening on port: %s" % config.HTTP_PORT
    try:
        srv.start()
    except KeyboardInterrupt:
        srv.stop()

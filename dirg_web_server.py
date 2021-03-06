# -*- coding: utf-8 -*-
from OpenSSL import SSL
import os
import json
from saml2.metadata import create_metadata_string
from dirg_web.InformationHandler import Information

from dirg_util.log import create_logger
from dirg_util.http_util import HttpHandler, Response


#External imports
import importlib
import argparse
from cherrypy import wsgiserver
from cherrypy.wsgiserver import ssl_pyopenssl
from beaker.middleware import SessionMiddleware
from mako.lookup import TemplateLookup


#Lookup for all mako templates.
from dirg_web.sp.handler import SpHandler
from dirg_web.util import SecureSession

LOOKUP = TemplateLookup(directories=['mako/templates',
                                     "/opt/dirg/dirg-util/mako/templates",
                                     'mako/htdocs'],
                        module_directory='mako/modules',
                        input_encoding='utf-8',
                        output_encoding='utf-8')

CACHE = {}

global username_password
username_password = open("auth/user_pass.json").read()
username_password = json.loads(username_password)

def application(environ, start_response):
    """
    WSGI application. Handles all requests.
    :param environ: WSGI enviroment.
    :param start_response: WSGI start response.
    :return: Depends on the request. Always a WSGI response where start_response first have to be initialized.
    """
    global username_password
    verification = False
    response = None

    session = SecureSession(environ, username_password)

    http_helper = HttpHandler(environ, start_response, session, logger)

    parameters = http_helper.query_dict()

    information = Information(environ, start_response, session, logger, parameters, LOOKUP, CACHE,
                              config.AUTHENTICATION_LIST , config.SQLITE_DB, config.EMAIL_CONFIG, sphandler,
                              config.ISSUER, config.IMAGE_FOLDER_PATH)

    path = http_helper.path()

    http_helper.log_request()

    if path=="refresh":
        username_password = open("auth/user_pass.json").read()
        username_password = json.loads(username_password)
        return Response("You have performed a refresh.")(environ, start_response)

    if http_helper.verify_static(path) or path.startswith(config.IMAGE_FOLDER_PATH):
        return http_helper.handle_static(path)
    elif information.verify(path):
        return information.handle(path)
    elif sphandler.verify_sp_requests(path):
        response = sphandler.handle_sp_requests(environ, start_response, path, session, parameters, information)
        verification = session.is_verification()

    if response is None:
        response = http_helper.http404()

    http_helper.log_response(response)
    session.verification(verification)
    return response


if __name__ == '__main__':
    #This is equal to a main function in other languages. Handles all setup and starts the server.

    #Read arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', dest='valid', default="4",
                        help="How long, in days, the metadata is valid from the time of creation")
    parser.add_argument('-c', dest='cert', help='certificate')
    parser.add_argument('-i', dest='id',
                        help="The ID of the entities descriptor in the metadata")
    parser.add_argument('-k', dest='keyfile',
                        help="A file with a key to sign the metadata with")
    parser.add_argument('-n', dest='name')
    parser.add_argument('-s', dest='sign', action='store_true',
                        help="sign the metadata")
    parser.add_argument('-sp', dest='sp_conf', default='sp_conf',
                        help="sp configuration file")
    parser.add_argument(dest="config")
    args = parser.parse_args()
    global config
    config = importlib.import_module(args.config)
    sp_config = importlib.import_module(args.sp_conf)

    global logger
    logger = create_logger(config.LOG_FILE)

    metadata = create_metadata_string("sp_conf.py", None, args.valid, args.cert, args.keyfile, args.id, args.name,
                                      args.sign)

    global sphandler
    sphandler = SpHandler(logger, metadata, os.path.dirname(os.path.abspath( __file__ )), args.sp_conf+".py", sp_config)

    global srv
    srv = wsgiserver.CherryPyWSGIServer(('0.0.0.0', config.PORT), SessionMiddleware(application, config.SESSION_OPTS))
    srv.stats['Enabled'] = True

    if config.HTTPS:
        srv.ssl_adapter = ssl_pyopenssl.pyOpenSSLAdapter(config.SERVER_CERT, config.SERVER_KEY, config.CERT_CHAIN)
        srv.ssl_adapter.context = srv.ssl_adapter.get_context()
        srv.ssl_adapter.context.set_options(SSL.OP_NO_SSLv3)
        srv.ssl_adapter.context.set_cipher_list('EDH+CAMELLIA:EDH+aRSA:EECDH+aRSA+AESGCM:EECDH+aRSA+SHA256:EECDH:+CAMELLIA128:+AES128:+SSLv3:!aNULL:!eNULL:!LOW:!3DES:!MD5:!EXP:!PSK:!DSS:!RC4:!SEED:!IDEA:!ECDSA:kEDH:CAMELLIA128-SHA:AES128-SHA')

    logger.info("Server starting")
    print "Server is listening on port: %s" % config.PORT
    try:
        srv.start()
    except KeyboardInterrupt:
        srv.stop()

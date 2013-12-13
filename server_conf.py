# -*- coding: utf-8 -*-
import os
from dirg_web.util import SecureSession
__author__ = 'haho0032'
#Port for the webserver.
PORT=4646
#True if HTTPS should be used instead of HTTP.
HTTPS=True

#URL to de server
BASEURL="localhost"
if HTTPS:
    BASEURL = "https://%s" % BASEURL
else:
    BASEURL = "http://%s" % BASEURL

#Full URL to the OP server
ISSUER = "%s:%s" % (BASEURL, PORT)

LOG_FILE="server.log"

#Beaker session configuration.
SESSION_OPTS = {
    'session.type': 'memory',
    'session.cookie_expires': True, #Expire when the session is closed.
    #'session.data_dir': './data',
    'session.auto': True,
    #'session.timeout' : 900 #Never expires only when the session is closed.
}


#If HTTPS is true you have to assign the server cert, key and certificate chain.
SERVER_CERT = "httpsCert/server.crt"
SERVER_KEY = "httpsCert/server.key"
#CERT_CHAIN="certs/chain.pem"
CERT_CHAIN = None

CONFIGFILES="configFiles"

IDPTESTENVIROMENT = [
    {
        "Name": "target2",
        "Description" : "Local IdP"
    },
    {
        "Name": "target",
        "Description" : "The new Local IdP"
    }
]

AUTHENTICATION_LIST = [
                        {"type": SecureSession.USERPASSWORD, "name": "Authenticate with username/password"},
                        {"type": SecureSession.SP, "name": "Authenticate with SAML"},
                      ]

SQLITE_DB = os.path.dirname(os.path.abspath( __file__ )) + "/sqlite.db"

EMAIL_CONFIG = {
    "base_url": ISSUER,
    "server": "",
    "from": "",
    "secure": True,
    "user_password": False,
    "username": "",
    "password": "",
    "from_name": "",
    "subject": "",
    "message_start": "",
    "message_end": ""
}

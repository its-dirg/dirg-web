# coding=utf-8
__author__ = 'haho0032'
import logging
import time
import re

from saml2.client import Saml2Client
from dirg_web.sp.util import SSO, ACS, Cache


#Log class for the SP.
logger = logging.getLogger(__name__)


#SPHandler represent a SP client and acts separate on the application server.
#The front end server can redirect to the sp to perform authentication.
#The method handleIdPResponse will give the correct response after authentication.
class SpHandler(object):
    """
    A SP client that performs authentication to a SAML IdP.
    """

    #The session name that holds the pyOpSamlProxy.client.sp.util.Cache object for the user.
    SPHANDLERSSOCACHE = "sphandlerssocache"

    def __init__(self, _logger, metadata, conf_dir, config_name, sp_conf):
        """
        Constructor for the SpHandler.
        :param _logger:     A logger.
        :param metadata:    Metadata XML text string. Represents a metadata file.
        :param conf_dir     Path to the configuration file for the service provider client(this class).
        :param config_name  Name of the configuration file for the service provider client(this class).
        :param sp_conf      The configuration file as an python object.
        """
        #Log class. (see import logging)
        self.logger = _logger
        #Metadata file
        self.metadata = metadata

        #Configurations for the SP handler. (pyOpSamlProxy.client.sp.conf)
        self.sp_conf = sp_conf
        #Name of the configuration file. See above.
        self.sp_conf_name = conf_dir + "/" + config_name
        #SP configuration object. (See project pysaml2; saml2.client.Saml2Client)
        self.sp = Saml2Client(config_file="%s" % self.sp_conf_name)
        #Extra arguments for the pyOpSamlProxy.client.sp.util.SSO object.
        #discosrv = URL to SAML discovery server.
        #wayf = URL to SAML WAYF server.
        self.args = {"discosrv": self.sp_conf.DISCOSRV, "wayf": self.sp_conf.WAYF}

    @staticmethod
    def verify_timeout(timeout):
        """
        Verifies if a timeout should occur. The method is static since it do not need the object to work.
        :param timeout: The last time before a timeout should occur.
                        Floating point number expressed in seconds since the epoch, in UTC
        :return: True if a timeout occurs, otherwise false.
        """
        if timeout is None or timeout < time.time():
            return True
        return False

    def verify_sp_requests(self, path):
        """
        Verifies if the sp is responsible for handling the request.
        :param path: The requested path.
        :return: True if this class should handle this request, otherwise false.
        """
        if path == "metadata":
            return True
        if re.search(self.sp_conf.DISCOENDPOINT, path):
            return True
        if re.search(self.sp_conf.SPVERIFYBASE, path):
            return True
        for regex in self.sp_conf.ASCVERIFYPOSTLIST:
            match = re.search(regex, path)
            if match is not None:
                return True
        for regex in self.sp_conf.ASCVERIFYREDIRECTLIST:
            match = re.search(regex, path)
            if match is not None:
                return True
        return False

    def handle_idp_response(self, response):
        """
        Takes care of the response from an Idp.

        :param response: Saml response. (see project pysaml2 saml2.response.AuthnResponse)

        :return: User identification (eduPersonPrincipalName)
        """
        #uid = response.assertion.subject.name_id.text
        uid = response.ava['eduPersonPrincipalName']
        if isinstance(uid, list):
            uid = uid[0]
        return uid

    def handle_sp_requests(self, environ, start_response, path, session, parameters, information_handler):
        """
        Handles all url:s that are intended for the sp.

        Can sign in a verified user and verify a new user.

        :param environ:             WSGI enviroment.
        :param start_response:      WSGI start response.
        :param path:                Requested path.
        :param session              Session object.
        :param parameters           Parameter dictionary from the request.
        :param information_handler  The handler class for the CMS application.

        :return: The response from the methods handle_idpverify and signin_idp in the InformationHandler.py class.
        """
        if path == "metadata":
            start_response('200 OK', [('Content-Type', "text/xml")])
            return self.metadata
        if "verify" in parameters and parameters["verify"] == "true":
            if "tag" in parameters:
                if "email" in parameters:
                    session.email(parameters["email"])
                else:
                    session.email(None)
                session.verification(True)
                session.verification_tag(parameters["tag"])

        if self.SPHANDLERSSOCACHE not in session or session[self.SPHANDLERSSOCACHE] is None:
            session[self.SPHANDLERSSOCACHE] = Cache()
        if re.search(self.sp_conf.SPVERIFYBASE, path) or re.search(self.sp_conf.SPVERIFYBASEIDP, path) \
            or re.search(self.sp_conf.DISCOENDPOINT, path):
            _sso = SSO(self.sp, environ, start_response, self.logger, session[self.SPHANDLERSSOCACHE], **self.args)
            return _sso.do()
        for regex in self.sp_conf.ASCVERIFYPOSTLIST:
            match = re.search(regex, path)
            if match is not None:
                acs = ACS(self.sp, environ, start_response, self.logger, session[self.SPHANDLERSSOCACHE])
                uid = self.handle_idp_response(acs.post())
                if session.is_verification():
                    session.verification(False)
                    return information_handler.handle_idpverify(session.email(), session.verification_tag(), uid)
                else:
                    #session.sign_in(uid, SecureSession.SP)
                    return information_handler.signin_idp(uid)
        for regex in self.sp_conf.ASCVERIFYREDIRECTLIST:
            match = re.search(regex, path)
            if match is not None:
                acs = ACS(self.sp, environ, start_response, self.logger, session[self.SPHANDLERSSOCACHE])
                uid = self.handle_idp_response(acs.redirect())
                if session.is_verification():
                    session.verification(False)
                    return information_handler.handle_idpverify(session.email(), session.verification_tag(), uid)
                else:
                    #session.sign_in(uid, SecureSession.SP)
                    return information_handler.signin_idp(uid)
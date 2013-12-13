from Carbon import List
from dirg_web.util import SecureSession

__author__ = 'haho0032'
import logging
import time
import re

from saml2.client import Saml2Client
from oic.utils.http_util import Redirect

from dirg_web.sp.util import SSO, ACS, Cache


#Log class for the SP.
logger = logging.getLogger(__name__)


#SPHandler represent a SP client and acts separate on the application server.
#The front end server can redirect to the sp to perform authentication.
#The method handleIdPResponse will give the correct response after authentication.
#The class SPAuthnMethodHandler is used to add SP authentication to the op server.
#The class UserInfoSpHandler is used to make it possible to return the attributes collected by SP for the op_server.
class SpHandler:
    #The session name that holds the pyOpSamlProxy.client.sp.util.Cache object for the user.
    SPHANDLERSSOCACHE = "sphandlerssocache"

    def __init__(self, logger, metadata, conf_dir, config_name, sp_conf):
        """
        Constructor for the SpHandler.
        :param logger: A logger.
        """
        #Log class. (see import logging)
        self.logger = logger
        #Metadata file
        self.metadata = metadata

        #Configurations for the SP handler. (pyOpSamlProxy.client.sp.conf)
        self.sp_conf = sp_conf
        #Name of the configuration file. See above.
        self.sp_conf_name = conf_dir + "/" + config_name
        #SP configuration object. (See project pysaml2; saml2.client.Saml2Client)
        self.sp = Saml2Client(config_file="%s" % self.sp_conf_name)
        #Extra arguments for the pyOpSamlProxy.client.sp.util.SSO object.
        self.ARGS = {}
        #URL to SAML discovery server.
        self.ARGS["discosrv"] = self.sp_conf.DISCOSRV
        #URL to SAML WAYF server.
        self.ARGS["wayf"] = self.sp_conf.WAYF

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

    def handleIdPResponse(self, response, cookie, session):
        """
        Takes care of the response from an Idp and saves the users attributes in a timed cache.
        :param response: Saml response. (see project pysaml2 saml2.response.AuthnResponse)
        :param cookie: The cookies sent by the client. A cookie string, same as environ["HTTP-COOKIE"]
        :param session: The current session for the user.
        :return: User identification
        """
        #uid = response.assertion.subject.name_id.text
        uid = response.ava['eduPersonPrincipalName']
        if isinstance(uid, list):
            uid = uid[0]
        #spHandlerCache = self.getSpHandlerCache(uid)
        #if spHandlerCache is None:
        #    spHandlerCache = SpHandlerCache()
        #    self.setSpHandlerCache(uid, spHandlerCache)
        #spHandlerCache.uid = uid
        #spHandlerCache.timeout = response.not_on_or_after
        #spHandlerCache.attributes = response.ava
        #spHandlerCache.auth = True
        return uid

    def handle_sp_requests(self, environ, start_response, path, session, parameters, information_handler):
        """
        Handles all url:s that are intended for the sp.
        :param environ: WSGI enviroment.
        :param start_response: WSGI start response.
        :return: The response created by underlying methods. For example;
                 Redirect to a discovery server.
                 Redirect to a SAML Idp.
                 URL to the authorization endpoint.
                 400 bad request.
        """
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
        if re.search(self.sp_conf.SPVERIFYBASE, path) or re.search(self.sp_conf.SPVERIFYBASEIDP, path):
            _sso = SSO(self.sp, environ, start_response, self.logger, session[self.SPHANDLERSSOCACHE], **self.ARGS)
            return _sso.do()
        for regex in self.sp_conf.ASCVERIFYPOSTLIST:
            match = re.search(regex, path)
            if match is not None:
                acs = ACS(self.sp, environ, start_response, self.logger, session[self.SPHANDLERSSOCACHE])
                uid = self.handleIdPResponse(acs.post(), environ["HTTP_COOKIE"], session)
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
                uid = self.handleIdPResponse(acs.redirect(), environ["HTTP_COOKIE"], session)
                if session.is_verification():
                    session.verification(False)
                    return information_handler.handle_idpverify(session.email(), session.verification_tag(), uid)
                else:
                    #session.sign_in(uid, SecureSession.SP)
                    return information_handler.signin_idp(uid)


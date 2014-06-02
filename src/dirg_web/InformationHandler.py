# -*- coding: utf-8 -*-
import json
import datetime
import time
import copy
import smtplib
from dirg_util.http_util import Response, ServiceError, Redirect
from dirg_web.util import SecureSession, DirgWebDbValidationException, DirgWebDb

__author__ = 'haho0032'


class Information(object):
    """
    This class handles all requests connected to the content, aka information, in the application.
    That includes authority and authentication for the information.
    """

    def __init__(self, environ, start_response, session, logger, parameters, lookup, cache, auth_methods, sqlite_db,
                 email_config, sphandler, base):
        """
        Constructor for the class.
        :param environ:        WSGI enviroment
        :param start_response: WSGI start_respose
        :param session:        Beaker session
        :param logger:         Class to perform logging.
        :param parameters:     Request parameters (POST or GET)
        :param lookup:               Lookup for mako templetes.
        :param cache:                A cache that lives as long as the application is shared between all users. (Dictionary)
        :param auth_methods:         A list of authentication methods. Example:
                               AUTHENTICATION_LIST = [
                                    {"type": SecureSession.USERPASSWORD, "name": "Authenticate with username/password"},
                                    {"type": SecureSession.SP, "name": "Authenticate with SAML"},
                               ]
        :param sqlite_db:            A full path to a sqlite database.
        :param email_config:         Configuration for a e-mail client. Example:
                                EMAIL_CONFIG = {
                                    "base_url": "http://localhost", #The application base url.
                                    "server": "smtp.test.com",        #Smtp server
                                    "from": "noreplay@test.com",    #From e-mail
                                    "secure": True,                 #True/False. If the TLS/SSL is used by the server.
                                    "user_password": False,         #True/False. If smtp server demands authentication.
                                    "username": "",                 #Username
                                    "password": "",                 #Password
                                    "from_name": "Test Tester",     #Name of the e-mail sender.
                                    "subject": "My subject",        #Subject for the e-mail.
                                    "message_start": "Hi!\n\nPlease click on the link below to activate your account.",
                                    "message_end": "Regards,\n\nThe support!"
                                }
        :param sphandler:       The class that acts as SAML client. /src/sp/handler.py.
        :base:                  Base url (context path) for the web application.
        """
        self.environ = environ
        self.start_response = start_response
        self.session = session
        self.logger = logger
        self.parameters = parameters
        self.lookup = lookup
        self.cache = cache
        self.auth_methods = auth_methods
        self.sqlite_db = sqlite_db
        self.email_config = email_config
        self.base = base
        self.sphandler = sphandler

        #The path the user will perform validation of an e-mail adress.
        self.verify_path = "/verify"

        #A requested parameter name for a tag in DirgWebDb database.
        self.param_tag = "tag"
        #A requested parameter name for a type in DirgWebDb database.
        self.param_type = "type"

        #Authentication method password.
        self.type_password = "pass"
        #Authentication method SAML IdP.
        self.type_idp = "idp"
        #Authentication method password. Only used for inviting a new user.
        self.type_password_new = "pass_new"
        #Authentication method SAML IdP.  Only used for inviting a new user.
        self.type_idp_new = "idp_new"

        #Folder for backing up content.
        self.backup_path = "backup/"
        #Folder for html content.
        self.information_path = "information/"
        #File ending for backing upp html content.
        self.file_ending = ".html"
        #The name and path to the menu file.
        self.menu_file = "menu/menu.json"
        #Name and path to the custom CSS style sheet that can be configured in the application.
        self.custom_css_file = "static/custom.css"
        #Cache key for all the banned users in the application.
        self.banned_users = "banned_users"

        #Contains all requested path this application will handle.
        self.urls = [
            "",
            "save",
            "information",
            "menu",
            "auth",
            "signin",
            "signout",
            "invite",
            "verify",
            "verifypass",
            "adminUsers",
            "changeUserAdmin",
            "changeUserValid",
            "deleteuser",
            "changepasswd",
            "file",
            "savefile",
            "information_init_app_js",
            "post_left_menu"
        ]

        #Init of the banned users space in the cache.
        #Banned users are all users that during a session is removed or banned.
        if self.banned_users not in self.cache:
            self.cache[self.banned_users] = {}

    def verify(self, path):
        """
        Verifies if a this class should handle the request.
        :param path: Requested path.
        :return: True if the class should handle the request, otherwise false.
        """
        for url in self.urls:
            if path == url:
                return True
        if path[:4] == "page":
            return True
        return False

    def handle(self, path):
        """
        Handles a request from the user.
        :param path: Requested path.
        :return: A WSGI response.
        """
        if self.session.email() is not None and self.session.email() in self.cache[self.banned_users]:
            self.handle_signout()
        if path == "information":
            if "page" in self.parameters:
                return self.handle_information(self.parameters["page"])
            return self.service_error("Page not found!")
        if path == "file":
            return self.handle_file()
        if path == "savefile":
            return self.handle_savefile()
        if path == "menu":
            return self.handle_menu(self.menu_file)
        if path == "save":
            return self.handle_save()
        if path == "auth":
            return self.handle_auth()
        if path == "signin":
            return self.handle_signin()
        if path == "signout":
            return self.handle_signout()
        if path == "invite":
            return self.handle_invite()
        if path == "verify":
            return self.handle_verify()
        if path == "verifypass":
            return self.handle_verifypass()
        if path == "adminUsers":
            return self.handle_admin_users()
        if path == "changeUserAdmin":
            return self.change_user_admin()
        if path == "changeUserValid":
            return self.change_user_valid()
        if path == "deleteuser":
            return self.delete_user()
        if path == "changepasswd":
            return self.change_passwd()
        if path[:4] == "page":
            return self.handle_viewpage(path)
        if path == "information_init_app_js":
            return self.handle_information_init_app_js()
        if path == "post_left_menu":
            return self.handle_post_left_menu()
        else:
            return self.handle_index()

    def handle_index(self):
        """
        Handles request to the index page and returns index.mako.
        :return: The index page as a WSGI response.
        """
        resp = Response(mako_template="index.mako",
                        template_lookup=self.lookup,
                        headers=[("Content-Security-Policy", "")])

        #("Content-Security-Policy", "script-src 'self'"),
        argv = {
        }
        return resp(self.environ, self.start_response, **argv)

    def handle_information_init_app_js(self):
        """
        Handles requests for the angular initiation javascript file.
        This file is created with mako to insert the correct context(base) path.
        :return A .js file as WSGI response.
        """
        resp = Response(mako_template="information_init_app_js.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "base": self.base
        }
        return resp(self.environ, self.start_response, **argv)

    def loadMenuDict(self):
        fp = open("menu/menu.json", 'r')
        text = fp.read()
        fp.close()
        return json.loads(text)

    def handle_post_left_menu(self):

        menuDict = self.loadMenuDict()
        menuDict['left'] = self.parameters['leftMenu']

        #Save menu
        myFile = open('menu/menu.json', 'w')
        myFile.write(json.dumps(menuDict))
        myFile.close()

        return self.return_json('{"asd": 0}')

    def dirg_web_db(self):
        """
        Initiates the DirgWebDb object, aka database for for the users in DIRG web.
        :return An instance of the class DirgWebDb.
        """
        db = DirgWebDb(self.sqlite_db, self.verify_path, self.param_tag, self.param_type, self.type_password,
                       self.type_idp)
        return db

    def signin_idp(self, uid):
        """
        When a user has signed in with the SAML SP client /src/sp/handler.py, it calls this method.
        Verifies if the saml user is registered in the application and will setup the session correct.
        :param uid: An unqiue identifier for the user.
        :return: A WSGI response. If successfull the user will be redirected to the start page, otherwise
                 will the user get an error page.
        """
        db = self.dirg_web_db()
        try:
            success, email = db.validate_uid(None, uid)
            if success:
                if email is not None:
                    self.session.email(email)
                user = db.user(email)
                self.session.sign_in(uid, SecureSession.SP, user)
                resp = Redirect("/")
                return resp(self.environ, self.start_response)
                #return self.handle_index()

        except Exception:
            pass
        resp = Response(mako_template="verify.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "_type": "none",
            "verification_message": "You are not allowed to use the application. Please apply for access.",
            "tag": ""
        }
        return resp(self.environ, self.start_response, **argv)

    def handle_idpverify(self, email, tag, uid):
        """
        When a user has verified the registered e-mail by login in to an SAML IdP, the user will
        be redirected to this method to finalize the regisration.
        :param email: The users e-mail.
        :param tag:   The unquie tag sent to the users e-mail adress.
        :param uid:   The unquie user identification returned from the SAML IdP.
        :return: A WSGI response to verify.mako.
        """
        try:
            db = self.dirg_web_db()
            if email is None:
                pass
            success, email = db.validate_uid(None, uid)
            if success:
                message = "You have already connected this IdP user with an e-mail in this application. " \
                          "Please contact an administrator."
            else:
                if email is None or db.email_exists(email):
                    if email is None:
                        email = db.email_from_tag(tag)
                    _type = db.verify_user(email, tag)
                    if _type not in [self.type_idp, self.type_password]:
                        message = "Invalid verification url. Please request for a new."
                    else:
                        db.add_uid_user(email, uid)
                        self.session.email(email)
                        user = db.user(email)
                        self.session.sign_in(uid, SecureSession.SP, user)
                        message = "You have successfully validated your e-mail and is now signed in."
                else:
                    message = "Your validation failed! You must type the correct e-mail address."
        except Exception:
            message = "Your validation failed! You must type the correct e-mail address."
        resp = Response(mako_template="verify.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "_type": "none",
            "verification_message": message,
            "tag": ""
        }
        return resp(self.environ, self.start_response, **argv)

    def change_password(self, tag_verification=False):
        """
        This method is used to change the users password.
        Requires that the paramaters email, password, password1 and password2 are sent as a request parameters.
        This method can be used to change password when the user is logged in to the application or during
        the verification phase.

        self.parameters["email"]:       The users e-mail.
        self.parameters["password"]:    The currenct password for the user.
        self.parameters["password1"]:   The new password for the user.
        self.parameters["password2"]:   The new password for the user.

        :param tag_verification: Tag sent to the users e-mail during the e-mail verification process.
        :return: A tuple (success, errormessage, type)
                    success: True if the password was changed.
                    errormessage: Empty if success = True otherwise a message describing the error.
                    type: Nothing or "pass" if the tag was correctly verified.
        """
        success = False
        errormessage = ""
        tag = ""
        tag_type = ""
        try:
            db = self.dirg_web_db()
            if "email" not in self.parameters or "password1" not in self.parameters or "password2" not in \
                    self.parameters or ("tag" not in self.parameters and tag_verification):
                errormessage = "Invalid request!"
                _type = "none"
            else:
                if tag_verification:
                    tag = self.parameters["tag"]
                    _type = db.verify_tag(tag)
                else:
                    _type = self.type_password
                if _type != self.type_password:
                    errormessage = "Invalid request!"
                    _type = "none"
                else:
                    password1 = self.parameters["password1"]
                    password2 = self.parameters["password2"]
                    if password1 != password2:
                        errormessage = "The passwords must be equal!"
                    else:
                        email = self.parameters["email"]
                        try:
                            db.validate_text_size("", "", "", 30, 12, password1)
                            try:
                                db.validate_email("", "", "", email)
                                if not db.email_exists(email):
                                    errormessage = "Not a valid e-mail!"
                                else:
                                    if tag_verification:
                                        tag_type = db.verify_user(email, tag)
                                    if tag_verification and tag_type != self.type_password:
                                        errormessage = "Invalid request!"
                                        _type = "none"
                                    else:
                                        db.change_password_user(email, password1)
                                        success = True
                                        _type = "none"
                            except DirgWebDbValidationException:
                                errormessage = "Not a valid e-mail!"
                        except DirgWebDbValidationException:
                            errormessage = "The password must consist of at least 12 and not more then 32 characters."
        except Exception:
            errormessage = "Invalid request!"
            _type = "none"

        return success, errormessage, _type

    def handle_verifypass(self):
        """
        Will verify the e-mail for a user that are going to user username/password as authentication.

        All request parameters are in self.parameters.

        Expects:
        self.parameters["tag"]:         The unquie tag sent to the users e-mail adress.
        self.parameters["email"]:       The users e-mail.
        self.parameters["password"]:    The currenct password for the user.
        self.parameters["password1"]:   The new password for the user.
        self.parameters["password2"]:   The new password for the user.
        :return: A WSGI response to the page verify.mako.
        """
        message = ""
        tag = ""
        if "tag" in self.parameters:
            tag = self.parameters["tag"]
        success, errormessage, _type = self.change_password(True)
        if _type == "none":
            message = errormessage
        if success:
            message = "Your account is now active!"

        resp = Response(mako_template="verify.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "_type": _type,
            "errormessage": errormessage,
            "verification_message": message,
            "tag": tag,
        }
        return resp(self.environ, self.start_response, **argv)

    def handle_verify(self):
        """
        Will verify the e-mail for an invited user.

        All request parameters are in self.parameters.

        Expects:
        self.parameters["tag"]:         The unquie tag sent to the users e-mail adress.
        :return: A WSGI response to verify.mako if the user will verify with username/password or a redirect
                 to a SAML IdP if the user will have to verify his identity with an IdP.
        """
        message = ""
        tag = ""
        if "tag" not in self.parameters:
            message = "Invalid verification url. Please request for a new."
            _type = "none"
        else:
            db = self.dirg_web_db()
            tag = self.parameters["tag"]
            _type = db.verify_tag(tag)
            if _type not in [self.type_idp, self.type_password]:
                message = "Invalid verification url. Please request for a new."
                _type = "none"
            else:
                _type = _type
                parameters = {"tag": tag, "verify": "true"}
                if _type == self.type_idp:
                    return self.sphandler.handle_sp_requests(self.environ, self.start_response,
                                                             self.sphandler.sp_conf.SPVERIFYBASE,
                                                             self.session, parameters, self)

        resp = Response(mako_template="verify.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "_type": _type,
            "verification_message": message,
            "tag": tag,
            "errormessage": ""
        }
        return resp(self.environ, self.start_response, **argv)

    def handle_invite(self):
        """
        Will a new user to the application and send a verification e-mail

        All request parameters are in self.parameters.

        Expects:
        self.parameters["email"]: The users e-mail, that will have to be verified.
        self.parameters["type"]: A string with values;
                                    pass        =   Invite existing user to sign in with username/password.
                                    idp         =   Invite existing user to sign in with SAML IdP.
                                    pass_new    =   Invite new user to sign in with username/password.
                                    idp_new     =   Invite new user to sign in with SAML IdP.
        self.parameters["forename"]: The users first name.
        self.parameters["surname"]:  The users last name.
        :return: A WSGI json response {text}. Will contain a text message if no errors occured.
                 If an error occure see service_error.
        """
        try:
            if not self.session.is_allowed_to_invite(self.cache[self.banned_users]):
                return self.service_error("You are not authorized!")
            if "email" not in self.parameters or "type" not in self.parameters:
                return self.service_error("Invalid request!")
            _type = self.parameters["type"]
            email = self.parameters["email"]
            db = self.dirg_web_db()
            try:
                db.validate_email("", "", "", email)
            except DirgWebDbValidationException as ex:
                return self.service_error("Not a valid e-mail!", ex)
            new_user = False
            if not db.email_exists(email):
                if _type not in [self.type_idp_new, self.type_password_new]:
                    return self.service_error("Invalid request!")
                if _type == self.type_idp_new:
                    _type = self.type_idp
                if _type == self.type_password_new:
                    _type = self.type_password
                if "forename" not in self.parameters or "surname" not in self.parameters:
                    return self.service_error("You must enter forename and surname for a new user.")
                forename = self.parameters["forename"]
                surname = self.parameters["surname"]
                try:
                    db.validate_text_size("", "", "", 30, 2, forename)
                    db.validate_text_size("", "", "", 30, 2, surname)
                except DirgWebDbValidationException as ex:
                    return self.service_error("Forename and surname must consist of 2 and is limited to 30 characters",
                                              ex)
                db.create_user(email, forename, surname)
                new_user = True
            else:
                if "forename" in self.parameters or "surname" in self.parameters:
                    return self.service_error("You should not enter forename and surname for an existing user!")
                user = db.user(email)
                forename = user["forename"].encode("UTF-8")
                surname = user["surname"].encode("UTF-8")
                if _type not in [self.type_idp, self.type_password]:
                    return self.service_error("Invalid request!")

            validation_url = self.email_config["base_url"] + db.create_verify_user(email, _type)

            sender = self.email_config["from"]
            receivers = [email]

            message = "From: " + self.email_config["from_name"] + " <" + self.email_config["from"] + ">\n"
            message += "To: " + forename + surname + " <" + email + ">\n"
            message += "Subject: " + self.email_config["subject"] + "\n"
            message += "\n"
            message += self.email_config["message_start"]
            message += "\n\n" + validation_url + "\n\n"
            message += self.email_config["message_end"]
            try:
                smtp_obj = smtplib.SMTP(self.email_config["server"])
                if self.email_config["secure"]:
                    smtp_obj.starttls()
                if self.email_config["user_password"]:
                    smtp_obj.login(self.email_config["username"], self.email_config["password"])
                smtp_obj.sendmail(sender, receivers, message)
            except Exception as ex:
                return self.service_error("Unable to send email!", ex)

            if new_user:
                if email in self.cache[self.banned_users]:
                    del self.cache[self.banned_users][email]
                return self.return_json("The user has been added and an invite is sent to the given e-mail.")
            return self.return_json("A new invite has been sent to the user.")
        except DirgWebDbValidationException as ex:
            return self.service_error("Invalid request!", ex, True)
        except Exception as ex:
            return self.service_error("Invalid request!", ex, True)

    def handle_save(self):
        """
        Will save the content for a CMS controlled web page.

        A web page get its unquie identification from the menu (/menu/menu.json).

        Each web page have a page identification called submit in menu.json.
        A web page can be a parent or child, there is no point to keep track of the relations.

        A web page can also contain a submenu. In that case each web page in the submenu must be connected to the
        page identification.

        Each submenu can contain several headers and the identifications within a submenu is never uqniqe.
        The combination of page, submenu header and submenu page must be unquie.

        All request parameters are in self.parameters.

        Expects:
        self.parameters["page"]:            The page (that can contain a submenu).
        self.parameters["html"]:            The html to be saved.
        self.parameters["submenu_header"]:  The unquie identifier for the submenu header. May be empty.
        self.parameters["submenu_page"]:    The unquie identifier for the submenu page. May be empty.
        :return: A WSGI json response {text}. The text will contain the saved HTML-file.
                 If an error occure see service_error.
        """
        if not self.session.is_allowed_to_edit_page(self.cache[self.banned_users]):
            return self.service_error("You are not authorized!")
        try:
            page = None
            html = None
            if "page" in self.parameters:
                page = self.parameters["page"]
            if "html" in self.parameters:
                html = self.parameters["html"]
            if page is None or html is None:
                return self.service_error("Invalid request!")
            page_ok, element = self.validate_page(page)

            submenu_header = ""
            submenu_page = ""

            if "submenu_header" in self.parameters and "submenu_page" in self.parameters:
                if len(self.parameters["submenu_header"]) > 0 and len(self.parameters["submenu_page"]) > 0:
                    submenu_header = "." + self.parameters["submenu_header"]
                    submenu_page = "." + self.parameters["submenu_page"]
                    submenu = self.get_submenu(page)
                    page_ok = self.validate_submenu(submenu, self.parameters["submenu_header"],
                                                    self.parameters["submenu_page"])

            if not page_ok:
                return self.service_error("Invalid request!")
            file_ = self.information_path + page + submenu_header + submenu_page + self.file_ending
            try:
                fp = open(file_, 'r')
                text = fp.read()
                fp.close()
                if len((text.strip())) > 0:
                    ts = time.time()
                    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    backup_file = self.backup_path + page + submenu_header + submenu_page + "_" + \
                                  timestamp + self.file_ending
                    fp = open(backup_file, 'w')
                    fp.write(text)
                    fp.close()
            except IOError:
                pass
            fp = open(file_, 'w')
            fp.write(html)
            fp.close()
            fp = open(file_, 'r')
            text = fp.read()
            fp.close()
            return self.return_json(text)
        except Exception as ex:
            return self.service_error("Invalid request!", ex, True)

    def handle_signin(self):
        """
        Handles username/password authtentication.

        All request parameters are in self.parameters.

        Expects:
        self.parameters["email"]:       The users e-mail.
        self.parameters["password"]:    Password for the given e-mail.
        :return: A WSGI json response. If an error occure see service_error.

        :return: A WSGI json response (see the method handle_auth). If an error occure see service_error.
        """
        try:
            if "user" in self.parameters and "password" in self.parameters:
                success = self.session.sign_in(self.parameters["user"], SecureSession.USERPASSWORD,
                                               None, self.parameters["password"])
                if not success:
                    db = self.dirg_web_db()
                    try:
                        valid = db.validate_password(self.parameters["user"], self.parameters["password"])
                    except DirgWebDbValidationException as ex:
                        return self.service_error("You are not authorized!")
                    if valid:
                        user = db.user(self.parameters["user"])
                        success = self.session.sign_in(self.parameters["user"], SecureSession.DBPASSWORD,
                                                       user, self.parameters["password"])
                if success:
                    self.session.email(self.parameters["user"])
                    return self.return_json(json.dumps(self.session.user_authentication(self.cache[self.banned_users])))
            return self.service_error("You are not authorized!")
        except Exception as ex:
            return self.service_error("The application is not working, please contact an administrator.", ex, True)

    def handle_signout(self):
        """
        Will log out the user from the application.

        The user WILL NOT be logged out from any SAML IdP's.
        :return: A WSGI json response (see the method handle_auth). If an error occure see service_error.
        """
        try:
            self.session.sign_out()
            return self.return_json(json.dumps(self.session.user_authentication(self.cache[self.banned_users])))
        except Exception as ex:
            return self.service_error("The application is not working, please contact an administrator.", ex, True)

    def handle_auth(self):
        """
        Will return the authorization in the application for the user in the session.

        This is not a security layer, it is only used for layout purpose.

        :return: A WSGI json response. If an error occure see service_error.
            Example:
            '{"authenticated": "true",
            "allowSignout": "true",
            "allowUserChange": "true",
            "allowedEdit": "true",
            "allowConfig": "false",
            "allowInvite": "true",
            "allowChangePassword": "true"}'

            Description:
            authenticated:       True if the user is authenticated.
            allowSignout:        True if the user can sign out from the application.
            allowUserChange:     True if the user is allowed to administrate users.
            allowedEdit:         True if the user is allowed to edit pages.
            allowConfig:         True if the user is allowed to configure menu and css files.
            allowInvite:         True if the user is allowed to invite other users.
            allowChangePassword: True if the user is allowed to change the password.
        """
        try:
            auth = self.session.user_authentication(self.cache[self.banned_users])
            auth["authMethods"] = self.auth_methods
            return self.return_json(json.dumps(auth))
        except Exception as ex:
            return self.service_error("The application is not working, please contact an administrator.", ex, True)

    def read_menu_into_cache(self, file_):
        """
        Will read the menu file(See /menu/menu_example.json) into the cache.

        :param file_ The path to the menu file. (See /menu/menu_example.json)
        :return: Nothing, the effect is that the menu is no in the cache.
        """
        text = open(file_).read()
        self.cache["menu"] = json.loads(text)

    def handle_menu(self, file_):
        """
        Will filter the menu for the current user, so only allowed menus will be showed for the user.
        :param file_ The path to the menu file. (See /menu/menu_example.json)
        :return A python object representation of the menu (See /menu/menu_example.json). The menu will be filtered.
                For example a user that is not authenticated will only see pages with the type: public.
        """
        try:
            self.read_menu_into_cache(file_)
            return self.return_json(json.dumps(self.filter_menu(copy.deepcopy(self.cache["menu"]))))
        except IOError as ex:
            return self.service_error("No menu file can be found!", ex, True)

    @staticmethod
    def find_page(page, menu):
        """
        Searches for a specific page in a menu and returns true if it exists.
        :param page: The submit identification for a page. (See /menu/menu_example.json)
        :param menu: A python object representation of the json menu. (See /menu/menu_example.json)
        :return True if the page exists in the menu, otherwise false.
        """
        if page == "":
            return False
        for element in menu:
            if "submit" in element and element["submit"] == page:
                return True, element
            if "children" in element:
                for child in element["children"]:
                    if "submit" in child and child["submit"] == page:
                        return True, child
        return False, None

    def filter_menu(self, menu):
        if menu is not None:
            if "left" in menu:
                menu["left"] = self.filter_menu_list(menu["left"])
            if "right" in menu:
                menu["right"] = self.filter_menu_list(menu["right"])
        return menu

    def filter_menu_list(self, menu):
        """
        Will filter a menu for a specific user.

        For example a user that is not authenticated will only see pages with the type: public.

        :param menu:  A python object representation of the json menu. (See /menu/menu_example.json)
        return The filtered menu.
        """
        tmp_menu = []
        if menu is not None:
            for tmp_element in menu:
                element = copy.deepcopy(tmp_element)
                if self.session.menu_allowed(element, self.cache[self.banned_users]):
                    tmp_menu.append(self.filter_submenu_list(element))
                    if "children" in element:
                        children = []
                        for tmp_child in element["children"]:
                            child = copy.deepcopy(tmp_child)
                            if self.session.menu_allowed(child, self.cache[self.banned_users]):
                                children.append(self.filter_submenu_list(child))
                        element["children"] = children
        return tmp_menu

    def filter_submenu_list(self, element):
        """
        Will filter a submenu for a specific user.

        For example a user that is not authenticated will only see submenu pages with the type: public.

        :param element:  Is an element in the menu that can hold a submenu.
        :return The element with a filtered submenu.
        """
        submenu_items = []
        if "submenu" in element:
            for tmp_submenu_item in element["submenu"]:
                list_items = []
                if "list" in tmp_submenu_item:
                    for tmp_list_item in tmp_submenu_item["list"]:
                        if self.session.menu_allowed(tmp_list_item, self.cache[self.banned_users]):
                            list_items.append(tmp_list_item)
                    if len(list_items) > 0:
                        tmp_submenu_item["list"] = list_items
                        submenu_items.append(tmp_submenu_item)
            element["submenu"] = submenu_items
        return element

    def validate_page(self, page):
        """
        Verifies if a user may view/save a given page.

        param: page The page to verify. Contains the value in submit in the menu json file.(See /menu/menu_example.json)

        :return True if user may see the page, otherwise false.
        """
        menu = self.get_menu()

        if menu is not None:
            page_ok = False
            element = None
            if "left" in menu:
                page_ok, element = self.find_page(page, menu["left"])
            if "right" in menu and page_ok is not True:
                page_ok, element = self.find_page(page, menu["right"])
            if not page_ok:
                page_ok = False
                element = None
            return page_ok, element
        return False, None

    def get_menu(self):
        """
        Returns a user filtered menu.

        For example a user that is not authenticated will only see pages with the type: public.

        return The filtered menu. A python object representation of the json menu. (See /menu/menu_example.json)
        """
        if "menu" not in self.cache or self.cache["menu"] is None:
            self.read_menu_into_cache(self.menu_file)
        menu = copy.deepcopy(self.cache["menu"])
        return self.filter_menu(menu)

    def get_submenu(self, page):
        """
        Retrieves the submenu for a page.

        :param page: The page that contains
                     Contains the value in submit in the menu json file.(See /menu/menu_example.json)

        :return None if the page do not have a submenu, otherwise a python object representation of the json submenu.
               (See /menu/menu_example.json)
        """
        menu = self.get_menu()
        submenu = None
        if menu is not None:
            submenu = self.find_submenu(page, menu["right"])
            if submenu is None:
                submenu = self.find_submenu(page, menu["left"])
        return submenu

    def find_submenu(self, page, menu):
        """
        Will search for a submenu in a page.

        return None if the page do not have a submenu, otherwise a python object representation of the json submenu.
               (See /menu/menu_example.json)
        """
        for element in menu:
            if "submit" in element and element["submit"] == page:
                if len(element["submenu"]) > 0:
                    return element["submenu"]
            if "children" in element:
                for child in element["children"]:
                    if child["submit"] == page:
                        return child["submenu"]
        return None

    def validate_submenu(self, submenu, header, page):
        """
        Verifies if a user may view/save a given submenu page.

        (See /menu/menu_example.json)

        param: submenu The submenu page to verify. Contains the value in submit in the submenu list.
        param: header The header for the submenu page. to verify. Contains the value in submit for the submenu.
        param: page The page to verify. Contains the value in submit for a parent or child.

        :return True if user may see the submenu page, otherwise false.
        """
        for tmp_submenu_item in submenu:
            if "submit" in tmp_submenu_item and tmp_submenu_item["submit"] == header:
                if "list" in tmp_submenu_item:
                    for tmp_list_item in tmp_submenu_item["list"]:
                        if "submit" in tmp_list_item and tmp_list_item["submit"] == page:
                            return True
        return False

    def get_information(self, page):
        """
        Retrives the HTML content for a CMS page.

        The following request parameters must be in self.parameters.

        Expects:
        self.parameters["submenu_header"]: If the page is in a submenu, then it contains the value in submit for the
                                           submenu. (See /menu/menu_example.json) May be empty.
        self.parameters["submenu_page"]:   If the page is in a submenu, then it contains the value in submit for the
                                           submenu list. (See /menu/menu_example.json) May be empty.


        param: page:                       The page to get html for. Contains the value in submit for a parent or child.
                                           (See /menu/menu_example.json)

        :return A tubple (exists, text, page, submenu_header, submenu_page)

        exists:         True if the page exists.
        text:           The HTML text.
        page:           See above.
        submenu_header: See above.
        submenu_page:   See above.

        """
        submenu_header = ""
        submenu_page = ""
        submenu_header_file = ""
        submenu_page_file = ""
        iframe_src = " "

        if self.session.is_page_set():
            page, submenu_header, submenu_page = self.session.get_page()
            self.parameters["submenu_header"] = submenu_header
            self.parameters["submenu_page"] = submenu_page
            self.session.clear_page()

        text = " "
        page_ok, element = self.validate_page(page)

        submenu = self.get_submenu(page)
        if "submenu_header" in self.parameters and "submenu_page" in self.parameters:
            if len(self.parameters["submenu_header"]) > 0 and len(self.parameters["submenu_page"]) > 0:
                submenu_header = self.parameters["submenu_header"]
                submenu_page = self.parameters["submenu_page"]
                submenu_header_file = "." + submenu_header
                submenu_page_file = "." + submenu_page
                page_ok = self.validate_submenu(submenu, self.parameters["submenu_header"],
                                                self.parameters["submenu_page"])
        else:
            if submenu is not None and len(submenu) > 0 and len(submenu[0]["list"]) > 0:
                if "submit" in submenu[0]:
                    submenu_header = submenu[0]["submit"]
                    submenu_header_file = "." + submenu_header
                if "list" in submenu[0] and "submit" in submenu[0]["list"][0]:
                    submenu_page = submenu[0]["list"][0]["submit"]
                    submenu_page_file = "." + submenu_page

        if not page_ok:
            return False, text, "", "", "", ""

        if "iframe_src" in element and len(element["iframe_src"]) > 0:
            text = " "
            iframe_src = element["iframe_src"]
        else:
            file_ = self.information_path + page + submenu_header_file + submenu_page_file + self.file_ending
            try:
                fp = open(file_, 'r')
                text = fp.read()
                if text == "":
                    text = " "
                fp.close()
            except IOError:
                fp = open(file_, 'w')
                fp.close()

        return True, text, page, submenu_header, submenu_page, iframe_src

    def handle_viewpage(self, path):
        """
        Makes it possible to view a specific page in the menu file. (See /menu/menu_example.json)

        Will save page, submenu_header and submenu_page in the session. When the index page is viewed it know
        what page to show.

        :param path: A path /page/{page}/{submenu_header}/{submenu_page} where {page} is a the submit value for a
                     child/parent in  the menu, {submenu_header} is the submit value for a submenu and
                     {submenu_page} is the submit value for list in a submenu. (See /menu/menu_example.json)

        return See method handle_index.
        """
        parameters = path.split("/")
        if len(parameters) == 2:
            page = parameters[1]
        elif len(parameters) == 4:
            page = parameters[1]
            self.parameters["submenu_header"] = parameters[2]
            self.parameters["submenu_page"] = parameters[3]
        else:
            return self.html_error("No such page can be found for you!")

        page_ok, text, page, submenu_header, submenu_page, iframe_src = self.get_information(page)
        if not page_ok:
            return self.html_error("No such page can be found for you!")

        self.session.setup_page(page, submenu_header, submenu_page)

        return self.handle_index()

    def handle_information(self, page):
        """
        Will return the information for a page child/parent/submenu.

        The following request parameters must be in self.parameters.

       Expects:
        self.parameters["submenu_header"]: If the page is in a submenu, then it contains the value in submit for the
                                           submenu. (See /menu/menu_example.json) May be empty.
        self.parameters["submenu_page"]:   If the page is in a submenu, then it contains the value in submit for the
                                           submenu list. (See /menu/menu_example.json) May be empty.

        param: page:                       The page to get html for. Contains the value in submit for a parent or child.
                                           (See /menu/menu_example.json)


        :return A WSGI json response {text}, where text is the html file. If an error occure see service_error.

        """
        page_ok, text, page, submenu_header, submenu_page, iframe_src = self.get_information(page)
        if not page_ok:
            return self.service_error("Invalid request!")

        data = {"html": text, "iframe_src": iframe_src,
                "page": page, "submenu_header": submenu_header, "submenu_page": submenu_page}

        return self.return_json(json.dumps(data))

    def handle_file(self):
        """
        This method verifies if the user may change the menu file and the custom css file.

        If the user may change them the content of the requested file will be returned.

        The following request parameters must be in self.parameters.

       Expects:
       self.parameters["name"]: Must be css for the custom css file and menu for the json menu.

       :return A WSGI text response, where text is the content of the file. The content is not wrapped in a json
               object.
               If an error occure see service_error.
        """
        try:
            if not self.session.is_allowed_to_change_file(self.cache[self.banned_users]):
                return self.service_error("You are not authorized!")
            try:
                if "name" in self.parameters:
                    name = self.parameters["name"]
                    if name == "css":
                        file_ = self.custom_css_file
                    elif name == "menu":
                        file_ = self.menu_file
                    else:
                        return self.service_error("File not found!", None, False, False)
                    text = " "
                    try:
                        fp = open(file_, 'r')
                        text = fp.read()
                        if text == "":
                            text = " "
                        fp.close()
                    except IOError:
                        pass
                    return self.return_text(text)
            except IOError as ex:
                return self.service_error("Invalid request!", ex, True, False)
        except Exception as ex:
            return self.service_error("Invalid request!", ex, True, False)

    def handle_savefile(self):
        """
        This method verifies if the user may save the menu file and the custom css file.

        Will save the given file, with the given content and then refresh the page for the user.

        The following request parameters must be in self.parameters.

       Expects:
       self.parameters["name"]:     Must be css for the custom css file and menu for the json menu.
       self.parameters["filetext"]: The content of the file.

       :return  A redirect to the index page.
                If an error occure see html_error.
        """
        try:
            if not self.session.is_allowed_to_change_file(self.cache[self.banned_users]):
                return self.html_error("You are not authorized!")
            try:
                if "name" in self.parameters and "filetext" in self.parameters:
                    name = self.parameters["name"][0]
                    filetext = self.parameters["filetext"][0]
                    if name == "css":
                        file_ = self.custom_css_file
                    elif name == "menu":
                        file_ = self.menu_file
                    else:
                        return self.html_error("Invalid request!")

                    text = ""
                    try:
                        fp = open(file_, 'r')
                        text = fp.read()
                        if text == "":
                            text = " "
                        fp.close()
                    except IOError:
                        pass

                    if len((text.strip())) > 0:
                        ts = time.time()
                        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                        backup_file = self.backup_path + name + "_" + timestamp
                        fp = open(backup_file, 'w')
                        fp.write(text)
                        fp.close()
                    fp = open(file_, 'w')
                    fp.write(filetext)
                    fp.close()
                    resp = Redirect("/")
                    return resp(self.environ, self.start_response)
            except IOError as ex:
                return self.html_error("Invalid request!", ex, True)
        except Exception as ex:
            return self.html_error("Invalid request!", ex, True)

    def return_text(self, text):
        """
        Returns the given text as conten type text/plain.

        :param text: A string.

        :return WSGI plain text response.
        """
        resp = Response(text, headers=[('Content-Type', "text/plain")])
        return resp(self.environ, self.start_response)

    def return_json(self, text):
        """
        Returns the given text as a content type application/json.

        :param: text: A json string.

        :return WSGI json response.
        """
        resp = Response(text, headers=[('Content-Type', "application/json")])
        return resp(self.environ, self.start_response)

    def service_error(self, message, exception=None, error=False, json_message=True):
        """
        Will return an error message as content type application/json or text/plain.

        Will log the error.

        :param message:     The message to be sent to the client.
        :param exception:   The exception that genererated the error, if it exists.
        :param error:       True if this is considered to be an error, otherwise false (warning).
        :json_message:      True if it should be return as json, otherwise false (plain text).

        return: WSGI json message {"ExceptionMessage": message} or a plain text message text.
        """
        if exception is not None:
            self.logger.error("Exception: ", exception)
        error_message = "Service error message: " + message
        if json_message:
            message = {"ExceptionMessage": message}

        if error:
            self.logger.error(error_message)
        else:
            self.logger.warning(error_message)
        if json_message:
            resp = ServiceError(json.dumps(message), headers=[('Content-Type', "application/json")])
        else:
            resp = ServiceError(message, headers=[('Content-Type', "text/plain")])
        return resp(self.environ, self.start_response)

    def html_error(self, message, exception=None, error=False):
        """
        Will return an error message as an html file.

        Will log the error.

        :param message:     The message to be sent to the client.
        :param exception:   The exception that genererated the error, if it exists.
        :param error:       True if this is considered to be an error, otherwise false (warning).

        return: WSGI response for the mako file html_error.mako.
        """
        if exception is not None:
            self.logger.error("Exception: ", exception)
        error_message = "Service error message: " + message
        if error:
            self.logger.error(error_message)
        else:
            self.logger.warning(error_message)
        resp = Response(mako_template="html_error.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "errormessage": message
        }
        return resp(self.environ, self.start_response, **argv)

    def change_user_valid(self):
        """
        Will change the "valid" status for a user. If a user is considered to be unvalid, the user is banned from
        the application.

        The following request parameters must be in self.parameters.

        Expects:
        self.parameters["email"]: The e-mail for the user.
        self.parameters["valid"]: 1 if the user is valid and 0 if the user is invalid.

        :return: A WSGI json response {text}. The text will contain a sucessfull message to the client.
                 If an error occure see service_error.
        """
        try:
            if not self.session.is_allowed_to_change_user(self.cache[self.banned_users]):
                return self.service_error("You are not authorized!")
            email = None
            valid = -1
            if "email" in self.parameters:
                email = self.parameters["email"]
            if "valid" in self.parameters:
                valid = self.parameters["valid"]

            if email is not None and (valid == 0 or valid == 1):
                db = self.dirg_web_db()
                if db.email_exists(email):
                    db.valid_user(email, valid)
                    if valid == 1:
                        if email in self.cache[self.banned_users]:
                            del self.cache[self.banned_users][email]
                        return self.return_json("User (" + email + ") is now a valid user.")
                    else:
                        self.cache[self.banned_users][email] = True
                        return self.return_json("User (" + email + ") is banned from the application.")
            return self.service_error("Invalid request!")
        except Exception as ex:
            return self.service_error("Invalid request!", ex, True)

    def delete_user(self):
        """
        Will permently remove a user from the application.

        The following request parameters must be in self.parameters.

        Expects:
        self.parameters["email"]: The e-mail for the user to be removed.

        :return: A WSGI json response {text}. The text will contain a sucessfull message to the client.
                 If an error occure see service_error.
        """
        try:
            if not self.session.is_allowed_to_change_user(self.cache[self.banned_users]):
                return self.service_error("You are not authorized!")
            email = None
            if "email" in self.parameters:
                email = self.parameters["email"]
            if email is not None:
                db = self.dirg_web_db()
                if db.email_exists(email):
                    self.cache[self.banned_users][email] = True
                    db.delete_user(email)
                    return self.return_json("User (" + email + ") is now removed from the application.")
            return self.service_error("Invalid request!")
        except Exception as ex:
            return self.service_error("Invalid request!", ex, True)

    def change_user_admin(self):
        """
        Will change the "admin" status for a user. If a user is considered to be admin, the user may administrate
        the application.

        The following request parameters must be in self.parameters.

        Expects:
        self.parameters["email"]: The e-mail for the user.
        self.parameters["admin"]: 1 if the user is admin, otherwise 0.

        :return: A WSGI json response {text}. The text will contain a sucessfull message to the client.
                 If an error occure see service_error.
        """
        try:
            if not self.session.is_allowed_to_change_user(self.cache[self.banned_users]):
                return self.service_error("You are not authorized!")
            email = None
            admin = -1
            if "email" in self.parameters:
                email = self.parameters["email"]
            if "admin" in self.parameters:
                admin = self.parameters["admin"]

            if email is not None and (admin == 0 or admin == 1):
                db = self.dirg_web_db()
                if db.email_exists(email):
                    db.admin_user(email, admin)
                    if admin == 1:
                        return self.return_json("User (" + email + ") is now administrator.")
                    else:
                        return self.return_json("User (" + email + ") is no longer administrator.")
            return self.service_error("Invalid request!")
        except Exception as ex:
            return self.service_error("Invalid request!", ex, True)

    def handle_admin_users(self):
        """
        Will list all user that can be administrated.


        :return A WSGI json response. If an error occure see service_error.

        Example response:
        [
            {
                "surname": "Last name",
                "admin": 1,                     #1 = administrator, otherwise 0.
                "verify": 0,                    #1 = e-mail is verified, otherwise 0.
                "email": "test.test@test.com",
                "valid": 1,                     #1 = valid user and 0 = banned user.
                "forename": "First name",
            },
        ]
        """
        try:
            if not self.session.is_allowed_to_change_user(self.cache[self.banned_users]):
                return self.service_error("You are not authorized!")
            db = self.dirg_web_db()
            users = db.list_all_users()
            tmp_users = []
            for user in users:
                tmp_user = {}
                tmp_user["surname"] = user["surname"]
                tmp_user["admin"] = user["admin"]
                tmp_user["verify"] = user["verify"]
                tmp_user["email"] = user["email"]
                tmp_user["valid"] = user["valid"]
                tmp_user["forename"] = user["forename"]
                tmp_users.append(tmp_user)

            return self.return_json(json.dumps(tmp_users))
        except Exception as ex:
            return self.service_error("Invalid request!", ex, True)

    def change_passwd(self):
        """
        Makes it possible for a user to change the password.

        Requires that the paramaters email, password, password1 and password2 are sent as request parameters.

        self.parameters["email"]:       The users e-mail.
        self.parameters["password"]:    The currenct password for the user.
        self.parameters["password1"]:   The new password for the user.
        self.parameters["password2"]:   The new password for the user.

        :return A WSGI json response {text}, where text is successfull message to the client.
                If an error occure see service_error.
        """
        try:
            if not self.session.is_allowed_to_change_password(self.cache[self.banned_users]):
                return self.service_error("You are not authorized!")
            db = self.dirg_web_db()
            try:
                if not db.validate_password(self.session.email(), self.parameters["password"]):
                    return self.service_error("You entered wrong current password!")
            except DirgWebDbValidationException as ex:
                return self.service_error("You entered wrong current password!", ex)
            self.parameters["email"] = self.session.email()
            success, error_message, _type = self.change_password()
            if success:
                return self.return_json("The password is changed!")
            else:
                return self.service_error(error_message)
        except Exception as ex:
            return self.service_error("Invalid request!", ex, True)

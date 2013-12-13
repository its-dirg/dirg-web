# -*- coding: utf-8 -*-
import json
import datetime
from smtplib import SMTPException
import time
import copy
import smtplib
from dirg_util.http_util import Response, ServiceError
from dirg_web.util import SecureSession, DirgWebDbValidationException, DirgWebDb

__author__ = 'haho0032'


class Information:


    def __init__(self, environ, start_response, session, logger, parameters, lookup, cache, auth_methods, sqlite_db,
                 email_config, sphandler):
        """
        Constructor for the class.
        :param environ:        WSGI enviroment
        :param start_response: WSGI start_respose
        :param session:        Beaker session
        :param logger:         Class to perform logging.
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
        self.sphandler = sphandler
        self.verify_path = "/verify"
        self.param_tag = "tag"
        self.param_type = "type"
        self.type_password = "pass"
        self.type_idp = "idp"
        self.type_password_new = "pass_new"
        self.type_idp_new = "idp_new"
        self.backup_path = "backup/"
        self.information_path = "information/"
        self.file_ending = ".html"
        self.menu_file = "menu/menu.json"
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
            "verifypass"
        ]

    def verify(self, path):
        for url in self.urls:
            if path == url:
                return True

    def handle(self, path):
        if path == "information":
            if "page" in self.parameters:
                return self.handle_information(self.parameters["page"])
            return self.service_error("Page not found!")
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
            return self.handle_verify(path)
        if path == "verifypass":
            return self.handle_verifypass()
        else:
            return self.handle_index()

    def handle_index(self):
        resp = Response(mako_template="index.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
        }
        return resp(self.environ, self.start_response, **argv)

    def dirg_web_db(self):
        db = DirgWebDb(self.sqlite_db, self.verify_path, self.param_tag, self.param_type, self.type_password,
                       self.type_idp)
        return db

    def signin_idp(self, uid):
        db = self.dirg_web_db()
        try:
            success, email = db.validate_uid(None, uid)
            if success:
                if email is not None:
                    self.session.email(email)
                self.session.sign_in(uid, SecureSession.SP)
                return self.handle_index()

        except Exception as ex:
            pass
        resp = Response(mako_template="verify.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "type": "none",
            "verification_message": "You are not allowed to use the application. Please apply for access.",
            "tag": ""
        }
        return resp(self.environ, self.start_response, **argv)

    def handle_idpverify(self, email, tag, uid):
        try:
            db = self.dirg_web_db()
            if email is None or db.email_exists(email) :
                if email is None:
                    email = db.email_from_tag(tag)
                type = db.verify_user(email, tag)
                if type not in [self.type_idp, self.type_password]:
                    message = "Invalid verification url. Please request for a new."
                else:

                    db.add_uid_user(email, uid)
                    self.session.email(email)
                    self.session.sign_in(uid, SecureSession.SP)
                    message = "You have successfully validated your e-mail and is now signed in."
            else:
                message = "Your validation failed! You must type the correct e-mail address."
        except:
            message = "Your validation failed! You must type the correct e-mail address."
        resp = Response(mako_template="verify.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "type": "none",
            "verification_message": message,
            "tag": ""
        }
        return resp(self.environ, self.start_response, **argv)

    def handle_verifypass(self):
        errormessage = ""
        message = ""
        type = self.type_password
        tag = ""
        try:
            db = self.dirg_web_db()
            if "email" not in self.parameters or "password1" not in self.parameters or "password2" not in self.parameters\
                or "tag" not in self.parameters:
                message = "Invalid verification request!"
                type = "none"
            tag = self.parameters["tag"]
            type = db.verify_tag(tag)
            if type != self.type_password:
                message = "Invalid verification request!"
                type = "none"
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
                                tag_type = db.verify_user(email, tag)
                                if tag_type != self.type_password:
                                    message = "Invalid verification request!"
                                    type = "none"
                                else:
                                    db.change_password_user(email, password1)
                                    message = "Your account is now active!"
                                    type = "none"
                        except DirgWebDbValidationException as ex:
                            errormessage = "Not a valid e-mail!"
                    except DirgWebDbValidationException as ex:
                        errormessage = "The password must consist of at least 12 and not more then 32 characters."
        except Exception as ex:
            message = "Invalid verification request!"
            type = "none"
        resp = Response(mako_template="verify.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "type": type,
            "errormessage": errormessage,
            "verification_message": message,
            "tag": tag,
        }
        return resp(self.environ, self.start_response, **argv)

    def handle_verify(self, path):
        message = ""
        tag = ""
        if "tag" not in self.parameters:
            message = "Invalid verification url. Please request for a new."
            type = "none"
        else:
            db = self.dirg_web_db()
            tag = self.parameters["tag"]
            type = db.verify_tag(tag)
            if type not in [self.type_idp, self.type_password]:
                message = "Invalid verification url. Please request for a new."
                type = "none"
            else:
                message = ""
                type = type
                parameters = {"tag": tag, "verify": "true"}
                if type == self.type_idp:
                    return self.sphandler.handle_sp_requests(self.environ, self.start_response,
                                                             self.sphandler.sp_conf.SPVERIFYBASE,
                                                             self.session,parameters, self)

        resp = Response(mako_template="verify.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "type": type,
            "verification_message": message,
            "tag": tag,
            "errormessage": ""
        }
        return resp(self.environ, self.start_response, **argv)

    def handle_invite(self):
        try:
            forename = ""
            surname = ""
            if "email" not in self.parameters or "type" not in self.parameters:
                return self.service_error("Invalid request!")
            type = self.parameters["type"]
            email = self.parameters["email"]
            db = self.dirg_web_db()
            try:
                db.validate_email("", "", "", email)
            except DirgWebDbValidationException as ex:
                return self.service_error("Not a valid e-mail!");
            new_user = False
            if not db.email_exists(email):
                if type not in [self.type_idp_new, self.type_password_new]:
                    return self.service_error("Invalid request!")
                if type == self.type_idp_new:
                    type = self.type_idp
                if type == self.type_password_new:
                    type = self.type_password
                if "forename" not in self.parameters or "surname" not in self.parameters:
                    return self.service_error("You must enter forename and surname for a new user.")
                forename = self.parameters["forename"]
                surname = self.parameters["surname"]
                try:
                    db.validate_text_size("", "", "", 30, 2, forename)
                    db.validate_text_size("", "", "", 30, 2, surname)
                except DirgWebDbValidationException as ex:
                    return self.service_error("Forename and surname must consist of 2 and is limited to 30 characters");
                db.create_user(email, forename, surname)
                new_user = True
            else:
                if "forename" in self.parameters or "surname" in self.parameters:
                    return self.service_error("You should not enter forename and surname for an existing user!")
                user = db.user(email)
                forename = user["forename"].encode("UTF-8")
                surname = user["surname"].encode("UTF-8")
                if type not in [self.type_idp, self.type_password]:
                    return self.service_error("Invalid request!")

            validation_url = self.email_config["base_url"] + db.create_verify_user(email, type)

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
                return self.service_error("Unable to send email!")

            if new_user:
                return self.return_json("The user has been added and an invite is sent to the given e-mail.")
            return self.return_json("A new invite has been sent to the user.")
        except DirgWebDbValidationException as ex:
            return self.service_error("Invalid request!");
        except Exception as ex:
            return self.service_error("Invalid request!")
        

    def handle_save(self):
        if not self.session.is_allowed_to_edit_page():
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
            page_ok = self.validate_page(page)
            if not page_ok:
                return self.service_error("Invalid request!")
            file_ = self.information_path + page + self.file_ending
            try:
                fp = open(file_, 'r')
                text = fp.read()
                fp.close()
                if len((text.strip())) > 0:
                    ts = time.time()
                    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    backup_file = self.backup_path + page + "_" + timestamp + self.file_ending
                    fp = open(backup_file, 'w')
                    fp.write(text)
                    fp.close()
            except IOError as ex:
                pass
            fp = open(file_, 'w')
            fp.write(html)
            fp.close()
            fp = open(file_, 'r')
            text = fp.read()
            fp.close()
            return self.return_json(text)
        except Exception:
            return self.service_error("Invalid request!")

    def handle_signin(self):
        try:
            if "user" in self.parameters and "password" in self.parameters:
                success = self.session.sign_in(self.parameters["user"], SecureSession.USERPASSWORD,
                                               self.parameters["password"])
                if not success:
                    db = self.dirg_web_db()
                    valid = db.validate_password(self.parameters["user"], self.parameters["password"])
                    success = self.session.sign_in(self.parameters["user"], SecureSession.DBPASSWORD,
                                               self.parameters["password"])
                if success:
                    return self.return_json(json.dumps(self.session.user_authentication()))
            return self.service_error("You are not authorized!")
        except Exception:
            return self.service_error("The application is not working, please contact an administrator.")


    def handle_signout(self):
        try:
            self.session.sign_out()
            return self.return_json(json.dumps(self.session.user_authentication()))
        except Exception:
            return self.service_error("The application is not working, please contact an administrator.")


    def handle_auth(self):
        try:
            auth = self.session.user_authentication();
            auth["authMethods"] = self.auth_methods;
            return self.return_json(json.dumps(auth))
        except Exception:
            return self.service_error("The application is not working, please contact an administrator.")

    def handle_menu(self, file_):
        try:
            text = open(file_).read()
            self.cache["menu"] = json.loads(text)
            return self.return_json(json.dumps(self.filter_menu(self.cache["menu"])))
        except IOError:
            return self.service_error("No menu file can be found!")

    @staticmethod
    def find_page(page, menu):
        if page == "":
            return False
        for element in menu:
            if element["submit"] == page:
                return True
            for child in element["children"]:
                if child["submit"] == page:
                    return True
        return False

    def filter_menu(self, menu):
        if menu is not None:
            if "left" in menu:
                menu["left"] = self.filter_menu_list(menu["left"])
            if "right" in menu:
                menu["right"] = self.filter_menu_list(menu["right"])
        return menu

    def filter_menu_list(self, menu):
        tmp_menu = []
        if menu is not None:
            for tmp_element in menu:
                element = copy.deepcopy(tmp_element)
                if self.session.menu_allowed(element):
                    tmp_menu.append(element)
                    if "children" in element:
                        children = []
                        for tmp_child in element["children"]:
                            child = copy.deepcopy(tmp_child)
                            if self.session.menu_allowed(child):
                                children.append(child)
                        element["children"] = children
        return tmp_menu

    def validate_page(self, page):
        if "menu" not in self.cache or self.cache["menu"] is None:
            self.handle_menu(self.menu_file)
        menu = self.cache["menu"]
        menu = self.filter_menu(menu)
        page_ok = False
        if "left" in menu:
            page_ok = self.find_page(page, menu["left"])
        if "right" in menu and page_ok is not True:
            page_ok = self.find_page(page, menu["right"])
        if not page_ok:
            page_ok = False
        return page_ok

    def handle_information(self, page):
        page_ok = self.validate_page(page)
        if not page_ok:
            return self.service_error("Invalid request!")
        file_ = self.information_path + page + self.file_ending
        try:
            fp = open(file_, 'r')
            text = fp.read()
            if text == "":
                text = " "
            fp.close()
            return self.return_json(text)
        except IOError as ex:
            fp = open(file_, 'w')
            fp.close()
            return self.return_json(" ")

    def return_json(self, text):
        resp = Response(text, headers=[('Content-Type', "application/json")])
        return resp(self.environ, self.start_response)


    def service_error(self, message):
        message = {"ExceptionMessage": message}
        resp = ServiceError(json.dumps(message))
        return resp(self.environ, self.start_response)

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
        self.custom_css_file = "static/custom.css"
        self.banned_users = "banned_users"
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
            "savefile"
        ]

        if self.banned_users not in self.cache:
            self.cache[self.banned_users] = {}

    def verify(self, path):
        for url in self.urls:
            if path == url:
                return True

    def handle(self, path):
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
            page_ok = self.validate_page(page)

            submeny_header = ""
            submeny_page = ""

            if "submeny_header" in self.parameters and "submeny_page" in self.parameters:
                if len(self.parameters["submeny_header"]) > 0 and len(self.parameters["submeny_page"]) > 0:
                    submeny_header = "." + self.parameters["submeny_header"]
                    submeny_page = "." + self.parameters["submeny_page"]
                    submenu = self.get_submenu(page)
                    page_ok = self.validate_submenu(submenu, self.parameters["submeny_header"],
                                                self.parameters["submeny_page"])

            if not page_ok:
                return self.service_error("Invalid request!")
            file_ = self.information_path + page + submeny_header + submeny_page + self.file_ending
            try:
                fp = open(file_, 'r')
                text = fp.read()
                fp.close()
                if len((text.strip())) > 0:
                    ts = time.time()
                    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    backup_file = self.backup_path + page + submeny_header + submeny_page + "_" + \
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
        try:
            self.session.sign_out()
            return self.return_json(json.dumps(self.session.user_authentication(self.cache[self.banned_users])))
        except Exception as ex:
            return self.service_error("The application is not working, please contact an administrator.", ex, True)

    def handle_auth(self):
        try:
            auth = self.session.user_authentication(self.cache[self.banned_users])
            auth["authMethods"] = self.auth_methods
            return self.return_json(json.dumps(auth))
        except Exception as ex:
            return self.service_error("The application is not working, please contact an administrator.", ex, True)

    def handle_menu(self, file_):
        try:
            text = open(file_).read()
            self.cache["menu"] = json.loads(text)
            return self.return_json(json.dumps(self.filter_menu(copy.deepcopy(self.cache["menu"]))))
        except IOError as ex:
            return self.service_error("No menu file can be found!", ex, True)

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
        submenu_items = []
        for tmp_submenu_item in element["submenu"]:
            list_items = []
            for tmp_list_item in tmp_submenu_item["list"]:
                if self.session.menu_allowed(tmp_list_item, self.cache[self.banned_users]):
                    list_items.append(tmp_list_item)
            if len(list_items) > 0:
                tmp_submenu_item["list"] = list_items
                submenu_items.append(tmp_submenu_item)
        element["submenu"] = submenu_items
        return element

    def validate_page(self, page):
        menu = self.get_menu()
        page_ok = False
        if "left" in menu:
            page_ok = self.find_page(page, menu["left"])
        if "right" in menu and page_ok is not True:
            page_ok = self.find_page(page, menu["right"])
        if not page_ok:
            page_ok = False
        return page_ok

    def get_menu(self):
        if "menu" not in self.cache or self.cache["menu"] is None:
            self.handle_menu(self.menu_file)
        menu = copy.deepcopy(self.cache["menu"])
        return self.filter_menu(menu)

    def get_submenu(self, page):
        menu = self.get_menu()
        submenu = self.find_submenu(page, menu["right"])
        if submenu is None:
            submenu = self.find_submenu(page, menu["left"])
        return submenu

    def find_submenu(self, page, menu):
        for element in menu:
            if element["submit"] == page:
                if len(element["submenu"]) > 0:
                    return element["submenu"]
            for child in element["children"]:
                if child["submit"] == page:
                    return child["submenu"]
        return None

    def validate_submenu(self, submenu, header, page):
        for tmp_submenu_item in submenu:
            if tmp_submenu_item["submit"] == header:
                for tmp_list_item in tmp_submenu_item["list"]:
                    if tmp_list_item["submit"] == page:
                        return True
        return False

    def handle_information(self, page):
        page_ok = self.validate_page(page)

        submeny_header = ""
        submeny_page = ""

        submenu = self.get_submenu(page)
        if "submeny_header" in self.parameters and "submeny_page" in self.parameters:
            if len(self.parameters["submeny_header"]) > 0 and len(self.parameters["submeny_page"]) > 0:
                submeny_header = "." + self.parameters["submeny_header"]
                submeny_page = "." + self.parameters["submeny_page"]
                page_ok = self.validate_submenu(submenu, self.parameters["submeny_header"],
                                                self.parameters["submeny_page"])
        else:
            if len(submenu) > 0 and len(submenu[0]["list"]) > 0:
                submeny_header = "." + submenu[0]["submit"]
                submeny_page = "." + submenu[0]["list"][0]["submit"]


        if not page_ok:
            return self.service_error("Invalid request!")
        file_ = self.information_path + page + submeny_header + submeny_page + self.file_ending
        try:
            fp = open(file_, 'r')
            text = fp.read()
            if text == "":
                text = " "
            fp.close()
            return self.return_json(text)
        except IOError:
            fp = open(file_, 'w')
            fp.close()
            return self.return_json(" ")

    def handle_file(self):
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
        resp = Response(text, headers=[('Content-Type', "text/plain")])
        return resp(self.environ, self.start_response)

    def return_json(self, text):
        resp = Response(text, headers=[('Content-Type', "application/json")])
        return resp(self.environ, self.start_response)

    def service_error(self, message, exception=None, error=False, json_message=True):
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
        try:
            if not self.session.is_allowed_to_change_user(self.cache[self.banned_users]):
                return self.service_error("You are not authorized!")
            db = self.dirg_web_db()
            users = db.list_all_users()
            return self.return_json(json.dumps(users))
        except Exception as ex:
            return self.service_error("Invalid request!", ex, True)

    def change_passwd(self):
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

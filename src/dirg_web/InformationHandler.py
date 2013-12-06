# -*- coding: utf-8 -*-
import json
import datetime
import time
import copy
from dirg_util.http_util import Response, ServiceError
from dirg_web.util import SecureSession

__author__ = 'haho0032'


class Information:
    def __init__(self, environ, start_response, session, logger, parameters, lookup, cache, auth_methods):
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
            "signout"
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
        else:
            return self.handle_index()

    def handle_index(self):
        resp = Response(mako_template="index.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
        }
        return resp(self.environ, self.start_response, **argv)

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

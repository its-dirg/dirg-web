# -*- coding: utf-8 -*-
from os.path import exists
import base64
from dirg_util.session import Session
import logging
import string
import hashlib
from validate_email import validate_email
from Crypto.Random import random

import sqlite3

__author__ = 'haho0032'

#Add a logger for this class.
logger = logging.getLogger("dirg_web_util")


class UnknownAuthenticationType(Exception):
    pass


class SecureSession(Session):
    SP = "sp"
    EMAIL = "email"
    VERIFICATION = "verification"
    VERIFICATION_TAG = "verification_tag"
    USERPASSWORD = "userpassword"
    DBPASSWORD = "dbpassword"
    AUTHENTICATED = "authenticated"
    AUTHENTICATION_TYPE = "authentication_type"
    ADMINISTRATOR = "administrator"
    MENU_TYPE = "type"
    MENU_PUBLIC = "public"
    MENU_PRIVATE = "private"
    MENU_CONSTRUCT = "construct"

    ALLOW_CHANGEPASSWORD = "allowChangePassword"
    ALLOW_INVITE = "allowInvite"
    ALLOW_CONFIG = "allowConfig"
    ALLOW_EDIT = "allowedEdit"
    ALLOW_USER_CHANGE = "allowUserChange"
    ALLOW_SIGN_OUT = "allowSignout"
    ALLOW_TRUE = "true"
    ALLOW_FALSE = "false"

    def __init__(self, environ, username_password):
        super(SecureSession, self).__init__(environ)
        if self.AUTHENTICATED not in self:
            self[self.AUTHENTICATED] = False
        if self.ADMINISTRATOR not in self:
            self[self.ADMINISTRATOR] = False
        self.username_password = username_password

    def email(self, email=None):
        if email is not None:
            self[self.EMAIL] = email
        if self.EMAIL not in self:
            return None
        return self[self.EMAIL]

    def verification_tag(self, tag=None):
        if tag is not None:
            self[self.VERIFICATION_TAG] = tag
        if self.VERIFICATION_TAG not in self:
            return None
        return self[self.VERIFICATION_TAG]

    def verification(self, verify):
        self[self.VERIFICATION] = verify

    def is_verification(self):
        if self.VERIFICATION not in self:
            return False
        return self[self.VERIFICATION]

    def is_authenticated(self):
        return self[self.AUTHENTICATED]

    def is_administrator(self):
        return self[self.ADMINISTRATOR]

    def is_allowed_to_change_user(self, banned_users):
        if self.email() in banned_users:
            return False
        if self.is_authenticated() and self.is_administrator():
            return True
        return False

    def is_allowed_to_invite(self, banned_users):
        if self.email() in banned_users:
            return False
        if self.is_authenticated() and self.is_administrator():
            return True
        return False

    def is_allowed_to_change_password(self, banned_users):
        if self.email() in banned_users:
            return False
        if self.is_authenticated() and self[self.AUTHENTICATION_TYPE] == self.USERPASSWORD:
            return True
        return False

    def is_allowed_to_change_file(self, banned_users):
        if self.email() in banned_users:
            return False
        if self.is_authenticated() and self.is_administrator():
            return True
        return False

    def is_allowed_to_edit_page(self, banned_users):
        if self.email() in banned_users:
            return False
        if self.is_authenticated() and self.is_administrator():
            return True
        return False

    def menu_allowed(self, menu, banned_users):
        if menu[self.MENU_TYPE] == self.MENU_PUBLIC:
            return True
        else:
            if self.email() in banned_users:
                return False

        if menu[self.MENU_TYPE] == self.MENU_PRIVATE and self.is_authenticated():
            return True

        if menu[self.MENU_TYPE] == self.MENU_CONSTRUCT and self.is_authenticated() and self.is_administrator():
            return True
        return False

    def sign_in(self, uid, _type, user=None, password=None):
        self[self.AUTHENTICATED] = False
        self[self.ADMINISTRATOR] = 0
        self[self.AUTHENTICATION_TYPE] = None
        if _type == self.SP:
            self[self.AUTHENTICATION_TYPE] = _type
            self[self.AUTHENTICATED] = True
            if user is not None and "admin" in user and user["admin"] == 1:
                self[self.ADMINISTRATOR] = True
        elif _type == self.USERPASSWORD and uid in self.username_password and self.username_password[uid] == password:
            self[self.AUTHENTICATION_TYPE] = _type
            self[self.AUTHENTICATED] = True
            self[self.ADMINISTRATOR] = True
        if _type == self.DBPASSWORD:
            self[self.AUTHENTICATION_TYPE] = self.USERPASSWORD
            self[self.AUTHENTICATED] = True
            if user is not None and "admin" in user and user["admin"] == 1:
                self[self.ADMINISTRATOR] = True
        return self[self.AUTHENTICATED]

    def sign_out(self):
        #Will not handle sign out for SSO with SAML!
        #if self[self.AUTHENTICATION_TYPE] == self.SP:
        #    return
        self[self.AUTHENTICATED] = False
        self[self.ADMINISTRATOR] = False
        self[self.AUTHENTICATION_TYPE] = None
        self[self.EMAIL] = None
        self[self.VERIFICATION_TAG] = None
        self[self.VERIFICATION] = None

    def user_authentication(self, banned_users):
        auth_object = {self.ALLOW_CHANGEPASSWORD: self.ALLOW_FALSE, self.ALLOW_SIGN_OUT: self.ALLOW_TRUE,
                       self.ALLOW_CONFIG: self.ALLOW_FALSE, self.ALLOW_INVITE: self.ALLOW_FALSE,
                       self.ALLOW_USER_CHANGE: self.ALLOW_FALSE}
        if self[self.AUTHENTICATED] and self.email() not in banned_users:
            auth_object[self.AUTHENTICATED] = self.ALLOW_TRUE
        else:
            auth_object[self.AUTHENTICATED] = self.ALLOW_FALSE
        if self[self.ADMINISTRATOR] and self.email() not in banned_users:
            auth_object[self.ALLOW_EDIT] = self.ALLOW_TRUE
            auth_object[self.ALLOW_INVITE] = self.ALLOW_TRUE
            auth_object[self.ALLOW_USER_CHANGE] = self.ALLOW_TRUE
        else:
            auth_object[self.ALLOW_EDIT] = self.ALLOW_FALSE
        if self.is_allowed_to_change_password(banned_users):
            auth_object[self.ALLOW_CHANGEPASSWORD] = self.ALLOW_TRUE
            #Will not handle sign out for SSO with SAML!
        #if self[self.AUTHENTICATION_TYPE] == self.SP:
        #    auth_object[self.ALLOW_SIGN_OUT] = self.ALLOW_FALSE
        return auth_object


class DirgWebDbValidationException(Exception):
    pass


class DirgWebDb(object):
    def __init__(self, db_name, verify_path, verify_param, type_param, password, idp):
        self.db_name = db_name.replace(".db", "") + ".db"
        self.verify_path = verify_path
        self.verify_param = verify_param
        self.type_param = type_param
        self.password = password
        self.idp = idp
        self.create_db()

    def create_validation_exception(self, table_name, row_id, column_name, message):
        log_message = "Database: + " + self.db_name + " \n" + \
                      "Table: " + table_name + "\n " + \
                      "Row: " + row_id + "\n " + \
                      "Column: " + column_name + "\n " + \
                      "Message: " + message + "\n "
        logging.error(log_message)
        raise DirgWebDbValidationException(message)

    def validate_text_size(self, table_name, row_id, column_name, _max, _min, text):
        if not (_min <= len(text) <= _max):
            message = "The length of the text " + text + " must be lesser or equal to " + str(_max) + \
                      " and greater or euqal to " + str(_min)
            self.create_validation_exception(table_name, row_id, column_name, message)

    def validate_email(self, table_name, row_id, column_name, email):
        if not validate_email(email):#,verify=True): A bit to slow
            message = "The email " + email + " is is not valid!"
            self.create_validation_exception(table_name, row_id, column_name, message)

    def db_connect(self):
        conn = sqlite3.connect(self.db_name)
        return conn

    def create_db(self):
        if not exists(self.db_name):
            conn = self.db_connect()
            try:
                c = conn.cursor()
                c.execute('''CREATE TABLE dirg_web_user (
                                                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              email TEXT UNIQUE,
                                                              password TEXT,
                                                              forename TEXT,
                                                              surname TEXT,
                                                              verify INTEGER,
                                                              valid INTEGER,
                                                              random_tag TEXT,
                                                              tag_type TEXT,
                                                              admin INTEGER
                                                            )
                              ''')
                c.execute('''CREATE TABLE dirg_web_uid (
                                                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              uid TEXT,
                                                              dirg_web_user_id INTEGER,
                                                              FOREIGN KEY(dirg_web_user_id) REFERENCES dirg_web_user(id)

                                                            )
                              ''')
                conn.commit()
                conn.close()
            finally:
                conn.close()


    def create_user(self, email, forename, surname):
        if not isinstance(email, unicode):
            email = unicode(email, "UTF-8")
        if not isinstance(forename, unicode):
            forename = unicode(forename, "UTF-8")
        surname = unicode(surname, "UTF-8")
        self.validate_email("dirg_web_user", "", "email", email)
        self.validate_text_size("dirg_web_user", "", "forename", 30, 2, forename)
        self.validate_text_size("dirg_web_user", "", "surname", 30, 2, surname)
        conn = self.db_connect()
        try:
            c = conn.cursor()
            c.execute('SELECT count(*) FROM dirg_web_user WHERE email=?', (email, ))
            response = c.fetchone()
            count = response[0]
            if count == 0:
                random_tag = "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(20))
                password = "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(20))
                sql = "INSERT INTO dirg_web_user(email, password, forename, surname, verify, valid," \
                      " random_tag, tag_type, admin) VALUES (?,?,?,?,?,?,?,?,?)"
                c.execute(sql, (email, password, forename, surname, 1, 1, random_tag, "none", 0))
                conn.commit()
            else:
                self.create_validation_exception("dirg_web_user", "", "email", "E-mail + " +
                                                                               email + " already exist!")
        finally:
            conn.close()

    def create_verify_user(self, email, _type):
        if not isinstance(email, unicode):
            email = unicode(email, "UTF-8")
        if not isinstance(_type, unicode):
            _type = unicode(_type, "UTF-8")
        random_tag = None
        if _type != self.password and _type != self.idp:
            self.create_validation_exception("", "", "", "No such type " + _type + " exists!")
        self.validate_email("dirg_web_user", "", "email", email)
        conn = self.db_connect()
        try:
            c = conn.cursor()
            c.execute('SELECT count(*) FROM dirg_web_user WHERE email=?', (email, ))
            response = c.fetchone()
            count = response[0]
            if count == 1:
                random_tag = "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(30))
                random_tag = base64.b64encode(random_tag)
                c.execute('UPDATE dirg_web_user SET verify = ?, random_tag = ?, tag_type = ? WHERE email=?',
                          (1, random_tag, _type, email))
                conn.commit()
            else:
                self.create_validation_exception("dirg_web_user", "", "email", "E-mail + " +
                                                                               email + " do not exist!")
            conn.close()
            return self.verify_path + "?" + self.verify_param + "=" + random_tag
        finally:
            conn.close()

    def verify_tag(self, tag):
        if not isinstance(tag, unicode):
            tag = unicode(tag, "UTF-8")
        conn = self.db_connect()
        try:
            c = conn.cursor()
            c.execute('SELECT count(*) FROM dirg_web_user WHERE random_tag=? AND tag_type <> ?',
                      (tag, "none"))
            response = c.fetchone()
            count = response[0]
            if count == 1:
                c.execute('SELECT tag_type FROM dirg_web_user WHERE random_tag=? AND tag_type <> ?',
                          (tag, "none"))
                response = c.fetchone()
                tag_type = response[0]
                conn.close()
                return tag_type
            else:
                conn.close()
                return None
        finally:
            conn.close()

    def verify_user(self, email, tag):
        if not isinstance(email, unicode) and email is not None:
            email = unicode(email, "UTF-8")
        if not isinstance(tag, unicode):
            tag = unicode(tag, "UTF-8")
        if email is not None:
            self.validate_email("dirg_web_user", "", "email", email)
        conn = self.db_connect()
        try:
            count = 0
            c = conn.cursor()
            if email is not None:
                c.execute('SELECT count(*) FROM dirg_web_user WHERE email=? AND random_tag=? AND tag_type <> ?',
                          (email, tag, "none"))
                response = c.fetchone()
                count = response[0]
            if count == 1:
                c.execute('SELECT tag_type FROM dirg_web_user WHERE email=? AND random_tag=? AND tag_type <> ?',
                          (email, tag, "none"))
                response = c.fetchone()
                tag_type = response[0]
                random_tag = "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(20))
                c.execute("UPDATE dirg_web_user SET verify = ?, random_tag = ?, tag_type = ? "
                          "WHERE email=?", (0, random_tag, "none", email))
                conn.commit()
                conn.close()
                return tag_type
            elif email is None:
                c.execute('SELECT tag_type FROM dirg_web_user WHERE random_tag=? AND tag_type <> ?',
                          (tag, "none"))
                response = c.fetchone()
                tag_type = response[0]
                random_tag = "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(20))
                c.execute("UPDATE dirg_web_user SET verify = ?, random_tag = ?, tag_type = ? "
                          "WHERE random_tag=?", (0, random_tag, "none", tag))
                conn.commit()
                conn.close()
                return tag_type
            else:
                conn.close()
                return None
        finally:
            conn.close()

    def validate_uid(self, email, uid):
        if email is not None:
            if not isinstance(email, unicode):
                email = unicode(email, "UTF-8")
        if not isinstance(uid, unicode):
            uid = unicode(uid, "UTF-8")
        self.validate_text_size("dirg_web_user", "", "password", 100, 5, uid)
        if email is not None:
            self.validate_email("dirg_web_user", "", "email", email)
        conn = self.db_connect()
        try:
            c = conn.cursor()
            count = 0
            if email is not None:
                c.execute('SELECT count(*) FROM dirg_web_user WHERE email=?', (email, ))
                response = c.fetchone()
                count = response[0]
            if count == 1:
                sql = 'SELECT count(*) FROM dirg_web_user dwu inner join dirg_web_uid dw_uid on dwu.id = ' \
                      'dw_uid.dirg_web_user_id WHERE dwu.email = ? and dw_uid.uid = ? and valid = ? and verify = ?'
                c.execute(sql, (email, uid, 1, 0))
                response = c.fetchone()
                password_count = response[0]
                conn.close()
                return password_count == 1, None
            elif email is None:
                sql = 'SELECT dwu.email FROM dirg_web_user dwu inner join dirg_web_uid dw_uid on dwu.id = ' \
                      'dw_uid.dirg_web_user_id WHERE dw_uid.uid = ? and valid = ? and verify = ?'
                c.execute(sql, (uid, 1, 0))
                response = c.fetchone()
                if response is None:
                    return False, None
                email = response[0]
                conn.close()
                return True, email
            else:
                return False, None
        finally:
            conn.close()

    def validate_password(self, email, password):
        if not isinstance(email, unicode):
            email = unicode(email, "UTF-8")
        if not isinstance(password, unicode):
            password_check = unicode(password, "UTF-8")
        else:
            password_check = password
        self.validate_text_size("dirg_web_user", "", "password", 30, 12, password_check)
        password = hashlib.sha224(base64.b64encode(password)).hexdigest()
        self.validate_email("dirg_web_user", "", "email", email)
        conn = self.db_connect()
        try:
            c = conn.cursor()
            c.execute('SELECT count(*) FROM dirg_web_user WHERE email=?', (email, ))
            response = c.fetchone()
            count = response[0]
            if count == 1:
                c.execute('SELECT count(*) FROM dirg_web_user WHERE email=? AND password = ? AND valid = ? '
                          'and verify = ?', (email, password, 1, 0))
                response = c.fetchone()
                password_count = response[0]
                conn.close()
                return password_count == 1
            else:
                self.create_validation_exception("dirg_web_user", "", "email", "E-mail + " +
                                                                               email + " do not exist!")
            conn.close()
            return False
        finally:
            conn.close()

    def email_from_tag(self, tag):
        conn = self.db_connect()
        try:
            c = conn.cursor()
            c.execute('SELECT email FROM dirg_web_user WHERE random_tag=? AND valid = ?', (tag, 1))
            response = c.fetchone()
            if response is None:
                return None
            return response[0]
        except Exception:
            return None
        finally:
            conn.close()

    def change_password_user(self, email, password):
        if not isinstance(email, unicode):
            email = unicode(email, "UTF-8")
        if not isinstance(password, unicode):
            password_check = unicode(password, "UTF-8")
        else:
            password_check = password
        self.validate_text_size("dirg_web_user", "", "password", 30, 12, password_check)
        password = hashlib.sha224(base64.b64encode(password)).hexdigest()
        self.validate_email("dirg_web_user", "", "email", email)
        conn = self.db_connect()
        try:
            c = conn.cursor()
            c.execute('SELECT count(*) FROM dirg_web_user WHERE email=?', (email, ))
            response = c.fetchone()
            count = response[0]
            if count == 1:
                c.execute("UPDATE dirg_web_user SET password = ? WHERE email=?", (password, email))
                conn.commit()
            else:
                self.create_validation_exception("dirg_web_user", "", "email", "E-mail + " +
                                                                               email + " do not exist!")
            conn.close()
        finally:
            conn.close()


    def add_uid_user(self, email, uid):
        if not isinstance(email, unicode):
            email = unicode(email, "UTF-8")
        if not isinstance(uid, unicode):
            uid = unicode(uid, "UTF-8")
        self.validate_text_size("dirg_web_user", "", "uid", 100, 5, uid)
        self.validate_email("dirg_web_user", "", "email", email)
        conn = self.db_connect()
        try:
            c = conn.cursor()
            c.execute('SELECT count(*) FROM dirg_web_user WHERE email=?', (email, ))
            response = c.fetchone()
            count = response[0]
            if count == 1:
                c.execute('SELECT id FROM dirg_web_user WHERE email=?', (email, ))
                response = c.fetchone()
                _id = response[0]
                c.execute("INSERT INTO dirg_web_uid(uid, dirg_web_user_id) VALUES (?,?)", (uid, _id))
                conn.commit()
            else:
                self.create_validation_exception("dirg_web_user", "", "email", "E-mail + " +
                                                                               email + " do not exist!")
            conn.close()
        finally:
            conn.close()


    def valid_user(self, email, valid=0):
        if not isinstance(email, unicode):
            email = unicode(email, "UTF-8")
        if valid != 1:
            valid = 0
        conn = self.db_connect()
        try:
            c = conn.cursor()
            c.execute('SELECT count(*) FROM dirg_web_user WHERE email=?', (email, ))
            response = c.fetchone()
            count = response[0]
            if count == 1:
                c.execute("UPDATE dirg_web_user SET valid = ? WHERE email=?", (valid, email))
                conn.commit()
            else:
                self.create_validation_exception("dirg_web_user", "", "email", "E-mail + " +
                                                                               email + " do not exist!")
            conn.close()
        finally:
            conn.close()

    def admin_user(self, email, admin=0):
        if not isinstance(email, unicode):
            email = unicode(email, "UTF-8")
        if admin != 1:
            admin = 0
        conn = self.db_connect()
        try:
            c = conn.cursor()
            c.execute('SELECT count(*) FROM dirg_web_user WHERE email=?', (email, ))
            response = c.fetchone()
            count = response[0]
            if count == 1:
                c.execute("UPDATE dirg_web_user SET admin = ? WHERE email=?", (admin, email))
                conn.commit()
            else:
                self.create_validation_exception("dirg_web_user", "", "email", "E-mail + " +
                                                                               email + " do not exist!")
            conn.close()
        finally:
            conn.close()

    def delete_user(self, email):
        if not isinstance(email, unicode):
            email = unicode(email, "UTF-8")
        conn = self.db_connect()
        try:
            c = conn.cursor()
            c.execute('SELECT count(*) FROM dirg_web_user WHERE email=?', (email, ))
            response = c.fetchone()
            count = response[0]
            if count == 1:
                c.execute("DELETE FROM dirg_web_user WHERE email=?", (email, ))
                conn.commit()
            else:
                self.create_validation_exception("dirg_web_user", "", "email", "E-mail + " +
                                                                               email + " do not exist!")
            conn.close()
        finally:
            conn.close()

    def email_exists(self, email):
        if not isinstance(email, unicode):
            email = unicode(email, "UTF-8")
        conn = self.db_connect()
        try:
            c = conn.cursor()
            c.execute('SELECT count(*) FROM dirg_web_user WHERE email=?', (email, ))
            response = c.fetchone()
            count = response[0]
            if count == 1:
                conn.close()
                return True
            else:
                conn.close()
                return False
        finally:
            conn.close()

    def clear_db(self):
        conn = self.db_connect()
        try:
            c = conn.cursor()
            c.execute('DELETE FROM dirg_web_user')
            c.execute('DELETE FROM dirg_web_uid')
            conn.commit()
            conn.close()
        finally:
            conn.close()

    def list_all_users(self):
        conn = self.db_connect()
        try:
            c = conn.cursor()
            query = 'SELECT rowid, dwu.id, dwu.email, dwu.password, dwu.forename, dwu.surname, dwu.verify, dwu.valid,' \
                    'dwu.random_tag, dwu.tag_type, dwu.admin FROM dirg_web_user dwu'
            c.execute(query)

            response_list = []
            response = c.fetchmany()
            while len(response) > 0:
                response_dict = {}
                response = response[0]
                response_dict["rowid"] = response[0]
                response_dict["id"] = response[1]
                response_dict["email"] = unicode(response[2].encode("UTF-8"), "UTF-8")
                response_dict["password"] = response[3]
                response_dict["forename"] = unicode(response[4].encode("UTF-8"), "UTF-8")
                response_dict["surname"] = unicode(response[5].encode("UTF-8"), "UTF-8")
                response_dict["verify"] = response[6]
                response_dict["valid"] = response[7]
                response_dict["random_tag"] = response[8]
                response_dict["tag_type"] = response[9]
                response_dict["admin"] = response[10]
                response_list.append(response_dict)
                response = c.fetchmany()
            conn.close()
            return response_list
        finally:
            conn.close()

    def user(self, email):
        if not isinstance(email, unicode):
            email = unicode(email, "UTF-8")
        self.validate_email("dirg_web_user", "", "email", email)
        conn = self.db_connect()
        try:
            c = conn.cursor()
            c.execute('SELECT count(*) FROM dirg_web_user WHERE email=?', (email, ))
            response = c.fetchone()
            count = response[0]
            if count == 1:
                c.execute('SELECT rowid, dwu.* FROM dirg_web_user dwu WHERE email=?', (email, ))
                response = c.fetchmany()
                while len(response) > 0:
                    response_dict = {}
                    response = response[0]
                    response_dict["rowid"] = response[0]
                    response_dict["id"] = response[1]
                    response_dict["email"] = unicode(response[2].encode("UTF-8"), "UTF-8")
                    response_dict["password"] = response[3]
                    response_dict["forename"] = unicode(response[4].encode("UTF-8"), "UTF-8")
                    response_dict["surname"] = unicode(response[5].encode("UTF-8"), "UTF-8")
                    response_dict["verify"] = response[6]
                    response_dict["valid"] = response[7]
                    response_dict["random_tag"] = response[8]
                    response_dict["tag_type"] = response[9]
                    response_dict["admin"] = response[10]
                    conn.close()
                    return response_dict
            else:
                self.create_validation_exception("dirg_web_user", "", "email", "E-mail + " +
                                                                               email + " do not exist!")
            conn.close()
        finally:
            conn.close()
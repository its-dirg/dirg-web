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
    """
    Exception when the type of authentication can not be identified.
    Support for now is username/password and SAML IdP
    """
    pass


class SecureSession(Session):
    """
    A session class that handles session authentication and authorization for the users.
    """

    #Key for SAML IdP authentication performed by a service provider (SP).
    SP = "sp"
    #Key for username/password authentication with the password file /auth/user_pass.json.
    USERPASSWORD = "userpassword"
    #Key for username/password authentication with a user in the database.
    DBPASSWORD = "dbpassword"

    #Key in the menu (see /menu/menu_example.json) for type of page.
    MENU_TYPE = "type"
    #Page type public. A page all users may view.
    MENU_PUBLIC = "public"
    #Page type private. A page only authenticated users may view.
    MENU_PRIVATE = "private"
    #Page type construct. A page only authenticated administrators may view.
    MENU_CONSTRUCT = "construct"

    #JSON true value
    ALLOW_TRUE = "true"
    #JSON false value
    ALLOW_FALSE = "false"


    #Key in the session for the users e-mail.
    EMAIL = "email"
    #Key in session. True if the user is performing a e-mail verification.
    VERIFICATION = "verification"
    #Key in session. Contains the tag used for verifying an e-mail
    VERIFICATION_TAG = "verification_tag"
    #Key in session. True if the user is authenticated.
    AUTHENTICATED = "authenticated"
    #Key in session. Contains how the user has been authenticated. self.USERPASSWORD or self.SP.
    AUTHENTICATION_TYPE = "authentication_type"
    #Key in session. True if the user is an administrator, otherwise false.
    ADMINISTRATOR = "administrator"
    #Key in session. Next page to be viewed by the user.
    DATA_PAGE = "data_page"
    #Key in session. Next submenu header to be viewed by the user.
    DATA_SUBMENU_HEADER = "data_submenu_heder"
    #Key in session. Next submenu page to be viewed by the user.
    DATA_SUBMENU_PAGE = "data_submenu_page"
    #Key in session. True if the user should view a specific pag, otherwise false.
    DATA_IS_SET = "data_is_set"
    #Key in session. True if the user is allowed to change password, otherwise false.
    ALLOW_CHANGEPASSWORD = "allowChangePassword"
    #Key in session. True if the user is allowed to invite antoher user, otherwise false.
    ALLOW_INVITE = "allowInvite"
    #Key in session. True if the user is allowed to edit menu and custom css, otherwise false.
    ALLOW_CONFIG = "allowConfig"
    #Key in session. True if the user is allowed to edit CMS pages, otherwise false.
    ALLOW_EDIT = "allowedEdit"
    #Key in session. True if the user is allowed to edit administrate users, otherwise false.
    ALLOW_USER_CHANGE = "allowUserChange"
    #Key in session. True if the user is allowed to sign out from the application, otherwise false.
    ALLOW_SIGN_OUT = "allowSignout"

    def __init__(self, environ, username_password):
        """
        Constructor for the class.

        :param environ              WSGI enviroment.
        :param username_password    /auth/user_pass.json as a python object.
        """
        super(SecureSession, self).__init__(environ)
        if self.AUTHENTICATED not in self:
            self[self.AUTHENTICATED] = False
        if self.ADMINISTRATOR not in self:
            self[self.ADMINISTRATOR] = False
        self.username_password = username_password

    def email(self, email=None):
        """
        Will set and return user e-mail in the session.

        :param e-mail: Will set the e-mail in the session. Ignores None objects.

        :return The e-mail saved in the session.
        """
        if email is not None:
            self[self.EMAIL] = email
        if self.EMAIL not in self:
            return None
        return self[self.EMAIL]

    def verification_tag(self, tag=None):
        """
        Set/retrieve the e-mail verification tag in the session.

        :param tag Will set the verification tag in the session. Ignores None objects.

        :return The verification tag in the session.
        """
        if tag is not None:
            self[self.VERIFICATION_TAG] = tag
        if self.VERIFICATION_TAG not in self:
            return None
        return self[self.VERIFICATION_TAG]

    def verification(self, verify):
        """
        Set in the session if the users is being verified or not.
        :param verify True if the user is in a e-mail verification process.

        """
        self[self.VERIFICATION] = verify

    def is_verification(self):
        """
        :return True if the current users e-mail is being verified, otherwise false.
        """
        if self.VERIFICATION not in self:
            return False
        return self[self.VERIFICATION]

    def is_authenticated(self):
        """
        return: True if the current user is authenticated, otherwise false.
        """
        return self[self.AUTHENTICATED]

    def is_administrator(self):
        """
        return: True if the user is administrator, otherwise false.
        """
        return self[self.ADMINISTRATOR]

    def is_allowed_to_change_user(self, banned_users):
        """
        return: True if the current user is allowed to administrate users, otherwise false.
        """
        if self.email() in banned_users:
            return False
        if self.is_authenticated() and self.is_administrator():
            return True
        return False

    def is_allowed_to_invite(self, banned_users):
        """
        return: True if the current user is allowed to invite users, otherwise false.
        """
        if self.email() in banned_users:
            return False
        if self.is_authenticated() and self.is_administrator():
            return True
        return False

    def is_allowed_to_change_password(self, banned_users):
        """
        return: True if the current user is allowed to change password, otherwise false.
        """
        if self.email() in banned_users:
            return False
        if self.is_authenticated() and self[self.AUTHENTICATION_TYPE] == self.USERPASSWORD:
            return True
        return False

    def is_allowed_to_change_file(self, banned_users):
        """
        return: True if the current user is allowed to change menu and the custom css file, otherwise false.
        """
        if self.email() in banned_users:
            return False
        if self.is_authenticated() and self.is_administrator():
            return True
        return False

    def is_allowed_to_edit_page(self, banned_users):
        """
        return: True if the current user is allowed to CMS pages, otherwise false.
        """
        if self.email() in banned_users:
            return False
        if self.is_authenticated() and self.is_administrator():
            return True
        return False

    def menu_allowed(self, menu, banned_users):
        """
        Verifies if a user may view a menu element.

        :param menu:         A menu page element.
        :param banned_users: All banned users in the system.

        return: True if the user may view the menu element, otherwise false.
        """
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
        """
        Signs in a user and will setup a correct session object.

        If the authentication _type is self.SP or self.DBPASSWORD the method expects the calling method to
        perform the actual authentication.

        For _type self.USERPASSWORD will this class perform the authentication.

        :param uid:      Unique identifier for the user, aka username.
        :param _type:    Type of authentication. self.SP, self.USERPASSWORD or self.DBPASSWORD.
        :param user:     Database user object.
                                Example: #(Show only relevant data needed)
                                    {
                                        "admin": 1,  #1 = administrator, otherwise 0.
                                    }
        :param password: Password. Only used for username/password authentications.
        """
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
        """
        Signs out the user from the application.
        Will not handle sign out for SSO with SAML!
        """
        #if self[self.AUTHENTICATION_TYPE] == self.SP:
        #    return
        self[self.AUTHENTICATED] = False
        self[self.ADMINISTRATOR] = False
        self[self.AUTHENTICATION_TYPE] = None
        self[self.EMAIL] = None
        self[self.VERIFICATION_TAG] = None
        self[self.VERIFICATION] = None

    def user_authentication(self, banned_users):
        """
        Returns a dictionary with the users application authority.

        :return: A dictionary.
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

    def setup_page(self, page, submenu_header, submenu_page):
        """
        Will save what page the user should view next.
        :param page:            The page (that can contain a submenu).
        :param submenu_header:  The unquie identifier for the submenu header. May be empty.
        :param submenu_page:    The unquie identifier for the submenu page. May be empty.
        """
        self[self.DATA_IS_SET] = True
        self[self.DATA_PAGE] = page
        self[self.DATA_SUBMENU_HEADER] = submenu_header
        self[self.DATA_SUBMENU_PAGE] = submenu_page

    def is_page_set(self):
        """
        :return True if the session contains the page the user should view, otherwise false.
        """
        return self[self.DATA_IS_SET]

    def clear_page(self):
        """
        Clears the page the user should view next.
        """
        self[self.DATA_IS_SET] = False
        self[self.DATA_PAGE] = ""
        self[self.DATA_SUBMENU_HEADER] = ""
        self[self.DATA_SUBMENU_PAGE] = ""

    def get_page(self):
        """
        :return The next page a user should view. A tuple (page, submenu_header, submenu_page)

        page:            The page (that can contain a submenu).
        submenu_header:  The unquie identifier for the submenu header. May be empty.
        submenu_page:    The unquie identifier for the submenu page. May be empty.
        """
        return self[self.DATA_PAGE], self[self.DATA_SUBMENU_HEADER], self[self.DATA_SUBMENU_PAGE]



class DirgWebDbValidationException(Exception):
    """
    Validation exception that occurs in the database.
    """
    pass


class DirgWebDb(object):
    """
    Handles communication with a sqlite database for dirg web.
    The database contains the users for dirg web.
    """

    def __init__(self, db_name, verify_path, verify_param, type_param, password, idp):
        """
        Constructor.

        param: db_name:         Name of the database.
        param: verify_path:     Url for e-mail verification in the application.
        param: verify_param:    Parameter name for the verification tag.
        param: type_param:      Parameter name for the type of authentication.
        param: password:        Parameter name for password authentication
        param: idp:             Parameter name for SAML IdP authentication.
        """
        self.db_name = db_name.replace(".db", "") + ".db"
        self.verify_path = verify_path
        self.verify_param = verify_param
        self.type_param = type_param
        self.password = password
        self.idp = idp
        self.create_db()

    def create_validation_exception(self, table_name, row_id, column_name, message):
        """
        Raises a validation exception and logs it as a warning.

        :param table_name:  Name of the table where the exception occured.
        :param row_id:      Row id.
        :param column_name: Column name.
        :param message:     Error message sent in the exception.
        """
        log_message = "Database: + " + self.db_name + " \n" + \
                      "Table: " + table_name + "\n " + \
                      "Row: " + row_id + "\n " + \
                      "Column: " + column_name + "\n " + \
                      "Message: " + message + "\n "
        logging.warning(log_message)
        raise DirgWebDbValidationException(message)

    def validate_text_size(self, table_name, row_id, column_name, _max, _min, text):
        """
        Validates that a text is of the correct length. If the text is correct nothing happens, oterwise
        will a DirgWebDbValidationException be raised.

        :param table_name:  Name of the table where the exception occured.
        :param row_id:      Row id.
        :param column_name: Column name.
        :param _max:        Max length of the text.
        :param _min:        Min length of the text.
        :param text:        The text to be validated.

        """
        if not (_min <= len(text) <= _max):
            message = "The length of the text " + text + " must be lesser or equal to " + str(_max) + \
                      " and greater or euqal to " + str(_min)
            self.create_validation_exception(table_name, row_id, column_name, message)

    def validate_email(self, table_name, row_id, column_name, email):
        """
        Validates that a e-mail is of the correct. If the e-mail is correct nothing happens, oterwise
        will a DirgWebDbValidationException be raised.

        :param table_name:  Name of the table where the exception occured.
        :param row_id:      Row id.
        :param column_name: Column name.
        :param e-mail:      E-mail to be validated.
        """
        if not validate_email(email):#,verify=True): A bit to slow
            message = "The email " + email + " is is not valid!"
            self.create_validation_exception(table_name, row_id, column_name, message)

    def db_connect(self):
        """
        :return A conenction to the sqlite 3 database.
        """
        conn = sqlite3.connect(self.db_name)
        return conn

    def create_db(self):
        """
        Will create a database with the correct tables if database do not exists.
        """
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
        """
        Creates a new user in the database.

        The user will get status unverfied, and must be verified before it is activated.

        :param email:       E-mail for the user.
        :param forename:    First name for the user.
        :param surname:     Last name for the user.
        """
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
        """
        Creates a verification URL the user can use to verify his e-mail.

        :param email: The user e-mail.
        :param _type: The type of authentication method. Must be the values sent to the constructor.

        :return A verification URL.
        """
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
        """
        Retrieves what kind of authentication that is connected to a specific verification tag.
        :param tag: A verification tag.

        :return Authentication type for the verification tag. Same value as added to the constructor.
        """
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
        """
        Verifies a user.

        :param email:   E-mail for the user. (Not needed, may be None)
        :param tag:     Verification tag.

        :return If the user is correctly verified it returns the type of authentication the user should use.
                If the user can not be verified, None is returned.
                Same value as added to the constructor.
        """
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
        """
        This is used for SAML IdP's or equals.

        Verifies if a unique identifier conencted to the users e-mail is saved in the database.

        The uid is the response given from a verified SAML IdP.

        :param email: The users e-mail adress. May be None.
        :param uid:   Unique identifier for the user.

        return A tuple (success, email)
                    success = True if the uid is successfully verifed, otherwise false.
                    email   = The email if the success is True and parameter email is None, otherwise None.
        """
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
        """
        Validates the password for a given e-mail.

        :param email:    The e-mail for a user.
        :param password: Password.

        return True if the e-mail/password combination is valid, otherwise false.
        """
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
        """
        Retrieves the e-mail for a given verification tag.

        :param tag: A verification tag.

        :return E-mail if it can e found, otherwise None.
        """
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
        """
        Changes the password for a user.

        :param email:       E-mail
        :param password:    New password.
        """
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
        """
        Connects a new unique user identification to an e-mail.
        This is used for connecting a SAML IdP to an e-mail.

        :param email: E-mail
        :param uid:   Unique user identification
        """
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
        """
        Can make a user valid or invalid. An invalid user is a banned user. To be authenticated a user must be valid.

        :param email: E-mail
        :param valid: 1 = valid and 0 = invalid.
        """
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
        """
        Set a user as administrator or remove administrator rights.

        :param email: E-mail
        :param admin: 1 = user get administrator priviliges and 0 = user looses administrator priviliges.
        """
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
        """
        Removes a user from the database.

        :param email: E-mail of the user to remove.
        """
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
        """
        Verifies if an e-mail exists in the database.

        :return True if the e-mail exists, otherwise false.
        """
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
        """
        Clear all tables in the database.
        """
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
        """
        List all users in the database.

        :return A list of all the users in the database.
            example:
                [
                    {
                        "rowid": "",        #Integer rowid
                        "id": "",           #Integer id
                        "email": "",        #E-mail
                        "password": "",     #Password hash
                        "forename": "",     #First name
                        "surname": "",      #Last name
                        "verify": "",       #Verify flag. 1 = Verified, otherwise 0.
                        "valid": "",        #Valid flag. 1 = valid and 0 = banned.
                        "random_tag": "",   #Verification tag.
                        "tag_type": "",     #How the user should be authenticated.
                        "admin": "",        #Admin flag. 1 = administrator and 0 = not administrator.
                    }
                ]
        """
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
        """
        Returns one user from the database.

        :param email: E-mail of the user.

        :return A user object..
            example:
                    {
                        "rowid": "",        #Integer rowid
                        "id": "",           #Integer id
                        "email": "",        #E-mail
                        "password": "",     #Password hash
                        "forename": "",     #First name
                        "surname": "",      #Last name
                        "verify": "",       #Verify flag. 1 = Verified, otherwise 0.
                        "valid": "",        #Valid flag. 1 = valid and 0 = banned.
                        "random_tag": "",   #Verification tag.
                        "tag_type": "",     #How the user should be authenticated.
                        "admin": "",        #Admin flag. 1 = administrator and 0 = not administrator.
                    }
        """
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
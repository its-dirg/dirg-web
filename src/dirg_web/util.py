from dirg_util.session import Session

__author__ = 'haho0032'

class UnknownAuthenticationType(Exception):
    pass

class SecureSession(Session):
    SP = "sp"
    USERPASSWORD = "userpassword"
    AUTHENTICATED = "authenticated"
    AUTHENTICATION_TYPE = "authentication_type"
    ADMINISTRATOR = "administrator"
    MENU_TYPE = "type"
    MENU_PUBLIC = "public"
    MENU_PRIVATE = "private"
    MENU_CONSTRUCT = "construct"

    ALLOW_CONFIG = "allowConfig"
    ALLOW_EDIT = "allowedEdit"
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

    def is_authenticated(self):
        return self[self.AUTHENTICATED]

    def is_administrator(self):
        return self[self.ADMINISTRATOR]

    def is_allowed_to_edit_page(self):
        if self.is_authenticated() and self.is_administrator():
            return True
        return False

    def menu_allowed(self, menu):
        if menu[self.MENU_TYPE] == self.MENU_PUBLIC:
            return True

        if menu[self.MENU_TYPE] == self.MENU_PRIVATE and self.is_authenticated():
            return True

        if menu[self.MENU_TYPE] == self.MENU_CONSTRUCT and self.is_authenticated() and self.is_administrator():
            return True
        return False

    def sign_in(self, uid, type, password = None):
        self[self.AUTHENTICATED] = False;
        if type == self.SP:
            self[self.AUTHENTICATION_TYPE] = type
            self[self.AUTHENTICATED] = True
        elif type == self.USERPASSWORD and uid in self.username_password and self.username_password[uid] == password:
            self[self.AUTHENTICATION_TYPE] = type
            self[self.AUTHENTICATED] = True
        else:
            self[self.AUTHENTICATION_TYPE] = None
        #self[self.ADMINISTRATOR] = administrator
        return self[self.AUTHENTICATED]

    def sign_out(self):
        #Will not handle sign out for SSO with SAML!
        if self[self.AUTHENTICATION_TYPE] == self.SP:
            return
        self[self.AUTHENTICATED] = False
        self[self.ADMINISTRATOR] = False

    def user_authentication(self):
        auth_object = {}
        auth_object[self.ALLOW_SIGN_OUT] = self.ALLOW_TRUE
        auth_object[self.ALLOW_CONFIG] = self.ALLOW_FALSE
        if self[self.AUTHENTICATED]:
            auth_object[self.AUTHENTICATED] = self.ALLOW_TRUE
        else:
            auth_object[self.AUTHENTICATED] = self.ALLOW_FALSE
        if self[self.ADMINISTRATOR]:
            auth_object[self.ALLOW_EDIT] = self.ALLOW_TRUE
        else:
            auth_object[self.ALLOW_EDIT] = self.ALLOW_FALSE
        #Will not handle sign out for SSO with SAML!
        if self[self.AUTHENTICATION_TYPE] == self.SP:
            auth_object[self.ALLOW_SIGN_OUT] = self.ALLOW_FALSE
        return auth_object
from dirg_util.session import Session

__author__ = 'haho0032'

class SecureSession(Session):
    def __init__(self, environ):
        super(SecureSession, self).__init__(environ)
        if "authenticated" not in self:
            self["authenticated"] = False
        if "administrator" not in self:
            self["administrator"] = False


    def is_authenticated(self):
        return self["authenticated"]

    def is_administrator(self):
        return self["administrator"]

    def is_allowed_to_edit_page(self):
        if self.is_authenticated() and self.is_administrator():
            return True
        return False

    def menu_allowed(self, menu):
        if menu["type"] == "public":
            return True

        if menu["type"] == "private" and self.is_authenticated():
            return True

        if menu["type"] == "construct" and self.is_authenticated() and self.is_administrator():
            return True
        return False

    def sign_in(self, administrator = False):
        self["authenticated"] = True
        self["administrator"] = administrator

    def sign_out(self):
        self["authenticated"] = False
        self["administrator"] = False

    def user_authentication(self):
        auth_object = {}
        auth_object["allowConfig"] = "false"
        if self["authenticated"]:
            auth_object["authenticated"] = "true"
        else:
            auth_object["authenticated"] = "false"
        if self["administrator"]:
            auth_object["allowedEdit"] = "true"
        else:
            auth_object["allowedEdit"] = "false"
        return auth_object
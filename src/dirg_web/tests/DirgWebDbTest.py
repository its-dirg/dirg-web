# -*- coding: utf-8 -*-

import unittest
from urlparse import parse_qs
import base64
import hashlib
from dirg_web.util import DirgWebDb, DirgWebDbValidationException

__author__ = 'haho0032'


class VerifyDirgWebDb(unittest.TestCase):

    def test_create_db(self):
        db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
        try:
            conn = db.db_connect()
            conn.close()
        except Exception as ex:
            self.fail(ex.message)

    def test_verify_email(self):
        db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
        ''' Not as hard e-mail control anymore
        try:
            db.validate_email("table_name", "row_id", "column_name", "notanemail@novalidurl.qwerty")
            self.fail("Should raise DirgWebDbValidationException")
        except DirgWebDbValidationException as ex:
            self.assertTrue("notanemail@novalidurl.qwerty" in ex.message)
        except Exception as ex:
            self.fail(ex.message)
        '''
        try:
            db.validate_email("table_name", "row_id", "column_name", "hans.horberg@umu.se")
        except Exception as ex:
            self.fail(ex.message)

    def test_verify_text(self):
        db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
        try:
            db.validate_text_size("table_name", "row_id", "column_name", 30, 2, "q")
            self.fail("Should raise DirgWebDbValidationException")
        except DirgWebDbValidationException as ex:
            self.assertTrue("30" in ex.message)
            self.assertTrue("2" in ex.message)
        except Exception as ex:
            self.fail(ex.message)
        try:
            db.validate_text_size("table_name", "row_id", "column_name", 4, 2, "qwerty")
            self.fail("Should raise DirgWebDbValidationException")
        except DirgWebDbValidationException as ex:
            self.assertTrue("4" in ex.message)
            self.assertTrue("2" in ex.message)
        except Exception as ex:
            self.fail(ex.message)
        try:
            db.validate_text_size("table_name", "row_id", "column_name", 30, 2, "qwerty")
        except Exception as ex:
            self.fail(ex.message)

    def test_create_user(self):
        try:
            db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
            db.clear_db()
            db.create_user("hans.horberg@umu.se", "Hans", "Hörberg")
            self.assertTrue(db.email_exists("hans.horberg@umu.se"))
            users = db.list_all_users()
            self.assertTrue(users is not None)
            self.assertTrue(len(users) == 1)
            self.assertTrue(users[0]["email"] == "hans.horberg@umu.se")
            self.assertTrue(len(users[0]["password"]) == 20)
            self.assertTrue(users[0]["forename"] == "Hans")
            self.assertTrue(users[0]["surname"] == unicode("Hörberg", "UTF-8") )
            self.assertTrue(users[0]["verify"] == 1)
            self.assertTrue(users[0]["valid"] == 1)
            self.assertTrue(len(users[0]["random_tag"]) == 20)
            self.assertTrue(users[0]["tag_type"] == "none")
            self.assertTrue(users[0]["admin"] == 0)
        except Exception as ex:
            self.fail(ex.message)

        try:
            db.create_user("hans.horberg@umu.se", "Hans", "Hörberg")
            self.fail("Should raise DirgWebDbValidationException")
        except DirgWebDbValidationException as ex:
            self.assertTrue("hans.horberg@umu.se" in ex.message)
        except Exception as ex:
            self.fail(ex.message)


        try:
            db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
            db.clear_db()
            db.create_user("hans.horberg@umu.se", "Hans", "Q")
            self.fail("Should raise DirgWebDbValidationException")
        except DirgWebDbValidationException as ex:
            self.assertTrue("Q" in ex.message)
        except Exception as ex:
            self.fail(ex.message)

        try:
            db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
            db.clear_db()
            db.create_user("hans.horberg@umu.se", "X", "Hörberg")
            self.fail("Should raise DirgWebDbValidationException")
        except DirgWebDbValidationException as ex:
            self.assertTrue("X" in ex.message)
        except Exception as ex:
            self.fail(ex.message)
        '''Not so hard e-mail control anymore.
        try:
            db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
            db.clear_db()
            db.create_user("hans.horberg@umu.qwerty", "X", "Hörberg")
            self.fail("Should raise DirgWebDbValidationException")
        except DirgWebDbValidationException as ex:
            self.assertTrue("hans.horberg@umu.qwerty" in ex.message)
        except Exception as ex:
            self.fail(ex.message)
        '''

        users = db.list_all_users()
        self.assertTrue(users is not None)
        self.assertTrue(len(users) == 0)

    def test_verify_user(self):
        db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
        db.clear_db()
        db.create_user("hans.horberg@umu.se", "Hans", "Hörberg")
        try:
            db.create_verify_user("hans.horberg@umu.se", "qwerty")
        except DirgWebDbValidationException as ex:
            self.assertTrue("qwerty" in ex.message)
        except Exception as ex:
            self.fail(ex.message)

        try:
            db.create_verify_user("hans.horberg@umu.qwerty", "idp")
        except DirgWebDbValidationException as ex:
            self.assertTrue("hans.horberg@umu.qwerty" in ex.message)
        except Exception as ex:
            self.fail(ex.message)

        try:
            users = db.list_all_users()
            tag_type = db.verify_user("hans.horberg@umu.se", users[0]["random_tag"])
            self.assertTrue(tag_type is None)
        except Exception as ex:
            self.fail(ex.message)

        try:
            users = db.list_all_users()
            verify_url = db.create_verify_user("hans.horberg@umu.se", "idp")
            split_str = verify_url.split("/verify?")
            self.assertTrue(len(split_str[0]) == 0)
            qs = parse_qs(split_str[1])
            tag_type = db.verify_user("daniel.evertsson@umu.se", qs["tag"][0])
            self.assertTrue(tag_type is None)
        except DirgWebDbValidationException as ex:
            self.assertTrue("hans.horberg@umu.qwerty" in ex.message)
        except Exception as ex:
            self.fail(ex.message)

        try:
            verify_url = db.create_verify_user("hans.horberg@umu.se", "idp")

            users = db.list_all_users()
            self.assertTrue(users is not None)
            self.assertTrue(len(users) == 1)
            self.assertTrue(users[0]["email"] == "hans.horberg@umu.se")
            self.assertTrue(len(users[0]["password"]) == 20)
            self.assertTrue(users[0]["forename"] == "Hans")
            self.assertTrue(users[0]["surname"] == unicode("Hörberg", "UTF-8") )
            self.assertTrue(users[0]["verify"] == 1)
            self.assertTrue(users[0]["valid"] == 1)
            self.assertTrue(len(base64.b64decode(users[0]["random_tag"])) == 30)
            self.assertTrue(users[0]["tag_type"] == "idp")
            self.assertTrue(users[0]["admin"] == 0)

            split_str = verify_url.split("/verify?")
            self.assertTrue(len(split_str[0]) == 0)
            qs = parse_qs(split_str[1])
            self.assertTrue(len(qs) == 1)
            self.assertTrue(len(base64.b64decode(qs["tag"][0])) == 30)

            tag_type = db.verify_user("hans.horberg@umu.se", qs["tag"][0])
            self.assertTrue(tag_type == "idp")

            users = db.list_all_users()
            self.assertTrue(users is not None)
            self.assertTrue(len(users) == 1)
            self.assertTrue(users[0]["email"] == "hans.horberg@umu.se")
            self.assertTrue(len(users[0]["password"]) == 20)
            self.assertTrue(users[0]["forename"] == "Hans")
            self.assertTrue(users[0]["surname"] == unicode("Hörberg", "UTF-8") )
            self.assertTrue(users[0]["verify"] == 0)
            self.assertTrue(users[0]["valid"] == 1)
            self.assertTrue(len(users[0]["random_tag"]) == 20)
            self.assertTrue(users[0]["tag_type"] == "none")
            self.assertTrue(users[0]["admin"] == 0)
        except Exception as ex:
            self.fail(ex.message)

    def test_change_password(self):
        try:
            db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
            db.clear_db()
            db.create_user("hans.horberg@umu.se", "Hans", "Hörberg")
            db.change_password_user("hans.horberg@umu.se", "qwertyuiopasdf")
            users = db.list_all_users()
            self.assertTrue(users[0]["password"] == hashlib.sha224(base64.b64encode("qwertyuiopasdf")).hexdigest())

            try:
                tag_type = db.change_password_user("hans.horberg@umu.se", "qwertyuiopasd")
            except DirgWebDbValidationException as ex:
                self.assertTrue("qwertyuiopasd" in ex.message)

            try:
                tag_type = db.change_password_user("hasse.horberg@umu.se", "qwertyuiopasdqwertryt")
            except DirgWebDbValidationException as ex:
                self.assertTrue("hasse.horberg@umu.se" in ex.message)

        except Exception as ex:
            self.fail(ex.message)

    def test_admin_user(self):
        try:
            db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
            db.clear_db()
            db.create_user("hans.horberg@umu.se", "Hans", "Hörberg")
            db.admin_user("hans.horberg@umu.se")
            users = db.list_all_users()
            self.assertTrue(users[0]["admin"] == 0)

            db.admin_user("hans.horberg@umu.se", 1)
            users = db.list_all_users()
            self.assertTrue(users[0]["admin"] == 1)

            db.admin_user("hans.horberg@umu.se", 0)
            users = db.list_all_users()
            self.assertTrue(users[0]["admin"] == 0)

        except Exception as ex:
            self.fail(ex.message)

    def test_valid_user(self):
        try:
            db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
            db.clear_db()
            db.create_user("hans.horberg@umu.se", "Hans", "Hörberg")
            db.valid_user("hans.horberg@umu.se")
            users = db.list_all_users()
            self.assertTrue(users[0]["valid"] == 0)

            db.valid_user("hans.horberg@umu.se", 1)
            users = db.list_all_users()
            self.assertTrue(users[0]["valid"] == 1)

            db.valid_user("hans.horberg@umu.se", 0)
            users = db.list_all_users()
            self.assertTrue(users[0]["valid"] == 0)

        except Exception as ex:
            self.fail(ex.message)


    def test_add_uid_user(self):
        try:
            db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
            db.clear_db()
            db.create_user("hans.horberg@umu.se", "Hans", "Hörberg")
            db.add_uid_user("hans.horberg@umu.se", "qwertyuiopasdf")
            valid, email = db.validate_uid("hans.horberg@umu.se", "qwertyuiopasdf")

            self.assertTrue(not valid)

            verify_url = db.create_verify_user("hans.horberg@umu.se", "idp")
            split_str = verify_url.split("/verify?")
            qs = parse_qs(split_str[1])
            tag_type = db.verify_user("hans.horberg@umu.se", qs["tag"][0])

            valid, email = db.validate_uid("hans.horberg@umu.se", "qwertyuiopasdf")
            self.assertTrue(valid)
        except Exception as ex:
            self.fail(ex.message)



    def test_validate_password(self):
        try:
            db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
            db.clear_db()
            db.create_user("hans.horberg@umu.se", "Hans", "Hörberg")
            db.create_user("daniel.evertsson@umu.se", "Hans", "Hörberg")
            db.create_user("roland.hedberg@adm.umu.se", "Roland", "Hedberg")

            db.change_password_user("roland.hedberg@adm.umu.se", "qwertyuiopasdf1234")

            db.change_password_user("daniel.evertsson@umu.se", "qwertyuiopasdf1234")

            db.change_password_user("hans.horberg@umu.se", "qwertyuiopasdf")
            db.change_password_user("hans.horberg@umu.se", "qwertyuiopasdf1234")

            valid = db.validate_password("hans.horberg@umu.se", "qwertyuiopasdf1234")
            self.assertTrue(not valid)

            verify_url = db.create_verify_user("hans.horberg@umu.se", "pass")
            split_str = verify_url.split("/verify?")
            qs = parse_qs(split_str[1])
            tag_type = db.verify_user("hans.horberg@umu.se", qs["tag"][0])

            valid = db.validate_password("hans.horberg@umu.se", "qwertyuiopasdf1234")
            self.assertTrue(valid)

            valid = db.validate_password("hans.horberg@umu.se", "qwertyuiopasdf")
            self.assertTrue(not valid)

            valid = db.validate_password("roland.hedberg@adm.umu.se", "qwertyuiopasdf1234")
            self.assertTrue(not valid)

            db.change_password_user("hans.horberg@umu.se", "j243234fdssdf#€#€#€SDFSDAF")
            valid = db.validate_password("hans.horberg@umu.se", "j243234fdssdf#€#€#€SDFSDAF")
            self.assertTrue(valid)

        except Exception as ex:
            self.fail(ex.message)

    def test_user(self):
        try:
            db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
            db.clear_db()
            db.create_user("hans.horberg@umu.se", "Hans", "Hörberg")

            user = db.user("hans.horberg@umu.se")
            self.assertTrue(user["email"] == "hans.horberg@umu.se")
            self.assertTrue(len(user["password"]) == 20)
            self.assertTrue(user["forename"] == "Hans")
            self.assertTrue(user["surname"] == unicode("Hörberg", "UTF-8") )
            self.assertTrue(user["verify"] == 1)
            self.assertTrue(user["valid"] == 1)
            self.assertTrue(len(user["random_tag"]) == 20)
            self.assertTrue(user["tag_type"] == "none")
            self.assertTrue(user["admin"] == 0)

        except Exception as ex:
            self.fail(ex.message)

    def test_validate_uid(self):
        try:
            db = DirgWebDb("test_db", "/verify", "tag", "type", "pass", "idp")
            db.clear_db()
            db.create_user("hans.horberg@umu.se", "Hans", "Hörberg")
            db.create_user("daniel.evertsson@umu.se", "Hans", "Hörberg")
            db.create_user("roland.hedberg@adm.umu.se", "Roland", "Hedberg")

            db.add_uid_user("roland.hedberg@adm.umu.se", "qwertyuiopasdf1234")
            db.add_uid_user("roland.hedberg@adm.umu.se", "qwertyuiopasdf12adssad")
            db.add_uid_user("roland.hedberg@adm.umu.se", "qwertyui")

            db.add_uid_user("daniel.evertsson@umu.se", "qwertyuiopasdf1234")
            db.add_uid_user("daniel.evertsson@umu.se", "qwertyuiopasdf12adssad")
            db.add_uid_user("daniel.evertsson@umu.se", "qwertyui")


            db.add_uid_user("hans.horberg@umu.se", "qwertyuiopasdf")
            db.add_uid_user("hans.horberg@umu.se", "qwertyuiopasdf1234")

            valid, email = db.validate_uid("hans.horberg@umu.se", "qwertyuiopasdf")
            self.assertTrue(not valid)

            verify_url = db.create_verify_user("hans.horberg@umu.se", "idp")
            split_str = verify_url.split("/verify?")
            qs = parse_qs(split_str[1])
            tag_type = db.verify_user("hans.horberg@umu.se", qs["tag"][0])

            valid, email = db.validate_uid("hans.horberg@umu.se", "qwertyuiopasdf")
            self.assertTrue(valid)

            valid, email = db.validate_uid("hans.horberg@umu.se", "qwertyuio")
            self.assertTrue(not valid)

            valid, email = db.validate_uid("roland.hedberg@adm.umu.se", "qwertyuiopasdf1234")
            self.assertTrue(not valid)

            db.add_uid_user("hans.horberg@umu.se", "j243234fdssdf#€#€#€SDFSDAF")
            valid, email = db.validate_uid("hans.horberg@umu.se", "j243234fdssdf#€#€#€SDFSDAF")
            self.assertTrue(valid)

            valid, email = db.validate_uid(None, "j243234fdssdf#€#€#€SDFSDAF")
            self.assertTrue(email == "hans.horberg@umu.se")
        except Exception as ex:
            self.fail(ex.message)
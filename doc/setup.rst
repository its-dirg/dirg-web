Setup
========

Setup of DIRG web
-----------------
To make this application work there are somethings you have to do.

Create menu.json
----------------
Go to your DIRG web folder and look in the folder menu. You have to create your basic menu file and name it menu.json. You can take a look at menu_example.json to understand the syntax.

Create server configuration
---------------------------
* Go to your DIRG web folder and copy the file server_conf.example to server_conf.py.
* If you want to use https you need certficates.
    * If you have access to production certificates you need to point them out. This is done by opening the file server_conf.py and point out all your certificates in the varaiables SERVER_CERT, SERVER_KEY and CERT_CHAIN.
    * If you do not have any production certificates you can generate self signed certificates by running the script [..]/httpsCert/create_key.sh. If you use this method the server_conf.py file need no changes.
    * To activate https you also need to set the variable HTTPS to True.
    * You must take a look at all the settings in server_conf.py and adjust them for your needs.
    * Set PORT to the port you want to use. If HTTPS is True, this is your https port.
    * If you use HTTPS you can also start a web server that redirects all the traffic to HTTPS. To give your http server the right port set the HTTP_PORT variable.
* If you are not using DIRG web on a local computer, update BASEURL to your IP or hostname.
* Do not forget to configure the variable EMAIL_CONFIG, which is used to invite people to login with federated login.
* All other variables should be understandable from their names and the comments.

Create Service Provider configuration
-------------------------------------
Copy the file sp_conf.example to sp_conf.py.

All configuration variables have describing comments, but here comes some addtional remarks.

If you have discovery or wayf server please update DISCOSRV and WAYF variables with the correct URL's.

PORT must be the same as in server_conf.py as well as the value of HTTPS.

BASEURL must be of the same value as server_conf.py.

If you do not have any production certifications you can generate self signed certificates by running the script [..]/sp_cert/create_key.sh.
If you use this method the attributes "key_file" and "cert_file "in sp_conf.py can remain unchanged, otherwise update them to the correct path of your certificates.

You can leave all the other configurations as they are. If you want to know more about the CONFIG variable, please read `pysaml2 documentations <https://dirg.org.umu.se/page/pysaml2>`_.


Login configurations
--------------------
* If you want to add user who can log in by username/passwords you have to edit the file [your path]/dirg-web/auth/user_pass.json


Federated login
---------------
First you need to make sure that you added the necessary info in sp_conf.py.

Generate the metadata for Dirg-web by running::

    ./create_metadata.sh

Don't forget to add the metadata in the IDP's configuration file.

Add federated user:
*******************

In order to make it possible for a user to login to Dirg-web using federated login the user most be invited.

**Note:** Server_conf.py most contain a working email configuration in order for the invite functionality to work.

#. Login in to Dirg-web by using any of the users specified in the file user_pass.json

#. Press Admin > Invite in the menu

#. Enter the users information

#. Send the invite

The invited user should now get an email containing a verification link.

It's possible to administrate users by pressing Admin > Administrate users

In the "Administrate users" view a list containing all the users will be presented. It will be possible to give a user specific permissions, activate a users account and see whether the user has verified the account or not.

**Note:** The user accounts specified in user_pass.json should only be uses to invite other users. When other users with admin privileges has been added all users listed in user_pass.json should be removed.
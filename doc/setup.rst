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
* Do not forget to configure the variable EMAIL_CONFIG.
* All other variables should be understandable from their names and the comments.

Create Service Provider configuration
-------------------------------------
Copy the file sp_conf.example to sp_conf.py.

All configuration variables have describing comments, but here comes some addtional remarks.

If you have discovery or wayf server please update DISCOSRV and WAYF variables with the correct URL's.

PORT must be the same as in server_conf.py as well as the value of HTTPS.

BASEURL must be of the same value as server_conf.py.

You can leave all the other configurations as they are. If you want to know more about the CONFIG variable, please read pysaml2 documentations.
===========
dirg-web
===========
The project dirg-web is a federated content management system based on bootstrap css and angularjs.

This is a lightweight CMS that allows you to build up a menu and add your content live on the page.

Functionality:

Federated login with SAML2.
Login with username/password with sqlite 3 database.
Login with username/password where users are defined in a json file.
Content management system.
Backup of CMS pages, menu and custom css.
Public pages for everyone.
Private pages for only authenticated users.
Pages under construct, only for administrators.
Dynamic menu that can be administrated on the web application.
CSS can be administrated on the web application.
Change password.
Invite only for private pages.
User administration.

TODO:
Create a small web application for administrating the menu. In the current version is the menu administrated from the application by modifying the json file.
Add search functionality on the page.
Add wiki functionallity.

INSTALL

dirg-web is based on dirg-util(https://github.com/its-dirg/dirg-util) and relies on the SAML implementation in pysaml2 (https://github.com/rohe/pysaml2).

For Linux and Raspberry PI user installation is made easy with the GIT project yais (https://github.com/its-dirg/yais).

To install without yais.

First install dirg-util annd pysaml2.

Make sure that you have all dependencies in setup.py installed.

Now install dirg-web:

git clone https://github.com/its-dirg/dirg-web [your path]
cd [your path]
sudo python setup.py install




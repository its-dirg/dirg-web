Install
========

Howto install DIRG web
----------------------
To install DIRG web is easy.
Linux/Mac::

    git clone https://github.com/its-dirg/dirg-web [your path]
    cd [your path]
    sudo python setup.py install

Dependencies
------------
Some dependencies may not be installed automatically.
You must also install dirg-util manually::

    git clone https://github.com/its-dirg/dirg-util [your path]
    cd [your path]
    sudo python setup.py install

Please look into `pysaml2 on github <https://github.com/rohe/pysaml2>`_ for more instructions.



Do you still have problems?
---------------------------
If you use linux (debian / raspberry pi) you can always use `yais <https://github.com/its-dirg/yais>`_ to install dirg-web.

To install dirg-web with yais, first follow the instructions on the yais web page.

Run **./yaisLinux.sh**

On the question "Do you want to install dirg-web (Y/n):", type Y. All other answers should be no (n).

The script will install everything you need.

With yais comes also a script to start/stop/restart the server.

**[dirg-web folder]/startDirgWeb.sh**

**[dirg-web folder]/stoptDirgWeb.sh**

**[dirg-web folder]/retDirgWeb.sh**
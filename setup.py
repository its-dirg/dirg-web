# coding=utf-8
from setuptools import setup

setup(
    name="dirg-web",
    version="0.1",
    description='DIRG web appplication. ',
    author = "Hans, Hoerberg",
    author_email = "hans.horberg@umu.se",
    license="Apache 2.0",
    packages=["dirg_web", "dirg_web/sp"],
    package_dir = {"": "src"},
    classifiers = ["Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Python Modules"],
    install_requires = ["cherrypy", "mako", "beaker", "validate_email", "pyDNS", 'Crypto', "pysaml2", "dirg-util"],
    zip_safe=False,
)
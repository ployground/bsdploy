Installation
============

Since bsdploy is still in development, there are currently no packaged versions available yet.

You can however install a development version from github or alpha releases from pypi.


Installing from PyPI
--------------------

Since bsdploy and its dependencies are written in Python, you can install them from the official Python Packaging Index (a.k.a. PyPI). 

To do so, you will need Python and virtualenv installed on your system, i.e. on Mac OS X using ``homebrew`` you would install ``brew install pyenv-virtualenv``.

Since bsdploy has specific requirements in regards to Fabric and ansible (meaning, their latest version will not always work with the latest version of bsdploy until the latter is adjusted) it is strongly recommended to install bsdploy into its own virtualenv, i.e. like so::

	virtualenv .
	bin/pip install bsdploy


Installing from github
----------------------

To follow along the latest version of bsdploy you will need the same requirements as listed above plus, obviously, ``git``. Then::

	git clone https://github.com/tomster/bsdploy.git
	cd bsdploy
	make

This will check out copies of bsdploy's immediate dependencies (``mr.awsome`` and friends) and create the ploy* executables inside ``bin``. You can either add the ``bin`` directory to your path or symlink them into somewhere that's already on your path.

Wo when keeping your checkout up-to-date it is usually a good idea to update the ``mr.awsome`` packages (located inside ``src``), as well. The best way to do so is to use the provided ``develop`` command like so::

	bin/develop up -v

The ``-v`` flag will show any git messages that arise during the update.
